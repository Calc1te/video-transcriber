from faster_whisper import WhisperModel
from enum import Enum
from pathlib import Path
from typing import Tuple
import subprocess
import json
import os
import logging
from utils import second_to_HMS
from ass_subtitle_generator import AssGenerator

class Device(Enum):
    cuda = 'cuda'
    cpu = 'cpu'

class VideoTranslator:
    def __init__(self, vid_path : str|Path , model_size : str, device : Device = Device.cpu, compute_type : str|None = None, verbose : bool = False):
        self.logger = logging.getLogger(__name__)
        self.model_size : str = model_size
        self.device : str = device.value
        self.workdir : str = os.getcwd()
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
            self.model = WhisperModel(self.model_size, device = self.device, compute_type = self.compute_type)
        except Exception as e:
            print(f"Error: {e}")
        
    def env_setup(self, dir : Path | None = None):
        self.base_dir = dir or os.getcwd()
        if dir == None:
            self.logger.warning('base directory not specified, using working directory...')
        for folder in ['wav', 'ass', 'out']:
            path = os.path.join(self.base_dir, folder)
            os.makedirs(path, exist_ok=True)
    def get_audio_stream(self):
        # ffmpeg -i movie.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 2 movie_audio.wav
        input = self.vid_path
        process = subprocess.Popen(['ffmpeg', '-i', input, '-vn', '-acodec', 'pcm_s16le', 
                                    '-ar', '44100', '-ac', '2', f'{self.workdir}/wav/{self.vid_name}_audio.wav'], stdout=subprocess.PIPE, text=True)
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        ret = process.poll()
        if ret != 0:
            self.logger.error(f'shit happened when generating transcript, error code {ret}')
        

    def get_resolution(self):
        # TODO: find a way to get res when extracting audio and get rid of this
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
        input_wav = f'{self.workdir}/wav/{self.vid_name}_audio.wav'
        transcriptions: list[Tuple[str, str, str]] = []
        try:
            segments, info = self.model.transcribe(input_wav, beam_size = 5)
            self.logger.info("Detected language '%s' with probability %f" % (info.language, info.language_probability))
            for segment in segments:
                self.logger.info("processing... now at '%3f'" % (segment.start))
                transcriptions.append((second_to_HMS(segment.start), second_to_HMS(segment.end), segment.text))
        except Exception as e:
            print(f'Error: {e}')
        self.transcriptions = transcriptions
        return transcriptions

    def generate_subtitle(self):
        self.ass = AssGenerator(self.vid_name,self.transcriptions)
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
    def singleVideoPipeline(self, translate : bool = False):
        if translate:
            self.logger.error("Error: Author haven't find any way to translate subtitle yet!")
            return
        self.get_audio_stream()
        self.get_resolution()
        self.whisper_transcription()
        self.generate_subtitle()
        self.compress_subtitle()


if __name__=='__main__':
    vidTr = VideoTranslator('0604.mp4','large-v3')
    vidTr.singleVideoPipeline(True)
    vidTr.singleVideoPipeline(False)