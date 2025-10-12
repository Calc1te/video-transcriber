from faster_whisper import WhisperModel
from enum import Enum
from pathlib import Path
from typing import Tuple, List
from utils import Transcription
import subprocess
import json
import os
import logging
from utils import second_to_HMS
from ass_subtitle_generator import AssGenerator, AssStyle

class Device(Enum):
    cuda = 'cuda'
    cpu = 'cpu'



class VideoTranslator:
    def __init__(self, vid_path : str|Path , model_size : str, device : Device = Device.cpu, compute_type : str|None = None, verbose : bool = False):
        self.env_ready : bool = False
        self.logger = logging.getLogger(__name__)
        self.model_size : str = model_size
        self.device : str = device.value
        self.env_setup()
        self.debug : bool = verbose
        self.vid_width : int = 1920
        self.vid_height : int = 1080
        if compute_type is not None:
            self.compute_type = compute_type
        else:
            self.compute_type = 'float16' if self.device == 'cuda' else 'int8'
            self.logger.warning(f'compute not specified, using {self.compute_type} as default')
        self.vid_path = vid_path if type(vid_path) == Path else Path(vid_path)
        self.vid_name = str(self.vid_path).split('/')[-1]
        try:
            self.logger.info("loading whisper model...")
            self.model = WhisperModel(self.model_size, device = self.device, compute_type = self.compute_type)
        except Exception as e:
            self.logger.error(f"Error: {e}")

    def env_setup(self, dir : Path | None = None):
        self.base_dir = dir or Path(os.getcwd())
        if dir == None:
            self.logger.warning('base directory not specified, using working directory...')
        for folder in ['wav', 'ass', 'out']:
            path = os.path.join(self.base_dir, folder)
            os.makedirs(path, exist_ok=True)
        self.out_dir = self.base_dir/'out'
        self.wav_dir = self.base_dir/'wav'
        self.ass_dir = self.base_dir/'ass'

    def get_audio_stream(self):
        # ffmpeg -i movie.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 1 movie_audio.wav
        input = self.vid_path
        try:
            process = subprocess.Popen(['ffmpeg', '-i', input, '-vn', '-acodec', 'pcm_s16le', 
                                        '-ar', '44100', '-ac', '1', f'{self.base_dir}/wav/{self.vid_name}_audio.wav'], stdout=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline() # type:ignore
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.logger.info(output.strip())
            ret = process.poll()
            if ret != 0:
                self.logger.error(f'shit happened when generating transcript, error code {ret}')
        except FileNotFoundError as e:
            self.logger.error(f"FFmpeg not found: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")

    def get_resolution(self):
        # TODO: find a way to get resolution when extracting audio and get rid of this
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "json",
            self.vid_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        info = json.loads(result.stdout)
        stream = info["streams"][0]
        self.vid_width = stream["width"]
        self.vid_height = stream["height"]

    def whisper_transcription(self):
        input_wav = f'{self.base_dir}/wav/{self.vid_name}_audio.wav'
        transcriptions: list[Transcription] = []
        try:
            segments, info = self.model.transcribe(input_wav, beam_size = 5)
            self.logger.info("Detected language '%s' with probability %f" % (info.language, info.language_probability))
            for segment in segments:
                self.logger.info("processing... now at '%3f'" % (segment.start))
                transcriptions.append(
                    Transcription(start=second_to_HMS(segment.start), 
                                end = second_to_HMS(segment.end), 
                                text = segment.text)
                    )
        except Exception as e:
            print(f'Error: {e}')
        self.transcriptions = transcriptions
        return transcriptions

    def split_transcription(self):
        self.translation_file = self.ass_dir / f'transcription_{Path(self.vid_name).stem}.json'
        # 构建包含元数据的导出数据
        export_data = {
            "metadata": {
                "video_path": str(self.vid_path),
                "video_name": self.vid_name,
                "width": self.vid_width,
                "height": self.vid_height,
                "model_size": self.model_size,
                "device": self.device,
                "compute_type": self.compute_type
            },
            "transcriptions": [
                {
                    "start": t.start,
                    "end": t.end,
                    "text": t.text,
                    "translation": ""
                }
                for t in self.transcriptions
            ]
        }
        
        with open(self.translation_file, 'w', encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=4)
        self.logger.info(f'Transcription and metadata saved to {self.translation_file}')

    def load_from_translation_file(self, translation_file: Path) -> bool:
        try:
            with open(translation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = data["metadata"]
            self.vid_path = Path(metadata["video_path"])
            self.vid_name = metadata["video_name"]
            self.vid_width = metadata["width"]
            self.vid_height = metadata["height"]
            
            self.transcriptions = []
            for t in data["transcriptions"]:
                trans = Transcription(
                    start=t["start"],
                    end=t["end"],
                    text=t["text"]
                )
                if t["translation"]:
                    trans.text = t["translation"] + '\n' + trans.text
                self.transcriptions.append(trans)
            
            self.translation_file = translation_file
            return True
        except Exception as e:
            self.logger.error(f"Failed to load translation file: {e}")
            return False

    def add_translation_to_subtitle(self):
        try:
            with open(self.translation_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for t, saved_t in zip(self.transcriptions, data["transcriptions"]):
                if saved_t["translation"]:
                    t.text = saved_t["translation"] + '\n' + t.text
            return True
        except FileNotFoundError:
            self.logger.error(f'Translation file not found: {self.translation_file}')
            return False
        except Exception as e:
            self.logger.error(f'Failed to read translation: {e}')
            return False
    def generate_subtitle(self, styles : List[AssStyle] | None = None):
        self.ass = AssGenerator(self.vid_name,self.transcriptions, styles)
        self.ass_path = self.ass.save(self.vid_width, self.vid_height)

    def compress_subtitle(self):
        # ffmpeg -i input.mp4 -vf "ass=subtitle.ass" -c:a copy output.mp4
        input_vid = self.vid_path
        ass_path = self.ass_path
        output_vid = f'out/w_sub_{self.vid_name}'

        if not os.path.exists(ass_path):
            raise FileNotFoundError(ass_path)
        import shlex
        cmd = [
            "ffmpeg",
            "-i", input_vid,
            "-vf", f"ass={shlex.quote(ass_path)}",
            "-c:a", "copy",
            output_vid
        ]
        subprocess.run(cmd, check=True)

    def singleVideoPipeline(self, manual_translate: bool = False, translation_file: Path | None = None):
        if translation_file and self.load_from_translation_file(translation_file):
            self.logger.info("Restored state from translation file")
            self.add_translation_to_subtitle()
            self.generate_subtitle()
            self.compress_subtitle()
            return
        
        self.get_audio_stream()
        self.get_resolution()
        self.whisper_transcription()
        
        if manual_translate:
            self.split_transcription()
            self.logger.info("Please translate the content in the generated file and run again with the translation file")
            return
        
        self.generate_subtitle()
        self.compress_subtitle()