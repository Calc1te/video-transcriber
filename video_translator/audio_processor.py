import numpy as np
from pathlib import Path
import wave
from typing import List, Tuple

def rms_to_db(rms) -> float:
    return 20 * np.log10(rms + 1e-10)

def cluster(periods: List[Tuple[float, float]], time_threshold: float = 0.2) -> List[Tuple[float, float]]:
    # just recall that this shit is not designed to be shown to user so fuck it
    if not periods:
        return []

    clustered = []
    start, end = periods[0]

    for next_start, next_end in periods[1:]:
        if next_start - end <= time_threshold:
            end = max(end, next_end)
        else:
            clustered.append((start, end))
            start, end = next_start, next_end
    clustered.append((start, end))

    return clustered

def detect_no_sound_period(audio: Path|str, threshold_db: int = -40, frame_size: int = 1024) -> List[Tuple[float, float]]:
    audio_path = Path(audio) if isinstance(audio, str) else audio
    
    try:
        with wave.open(str(audio_path), 'rb') as wav_file:
            n_channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            n_frames = wav_file.getnframes()
            
            audio_data = wav_file.readframes(n_frames)
        
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        
        if n_channels == 2:
            audio_np = audio_np.reshape(-1, 2).mean(axis=1).astype(np.int16)
        
        quiet_frames = []
        for i in range(0, len(audio_np) - frame_size, frame_size):
            frame = audio_np[i:i + frame_size].astype(np.float32) / 32768.0 # normalize rsm to [-1, 1]
            rms = np.sqrt(np.mean(frame ** 2) + 1e-10 )
            db = rms_to_db(rms)
            
            if db < threshold_db:
                quiet_frames.append(i)
        
        silent_periods = []
        if quiet_frames:
            start_frame = quiet_frames[0]
            prev_frame = quiet_frames[0]
            
            for frame_idx in quiet_frames[1:]:
                if frame_idx - prev_frame > frame_size:
                    end_frame = prev_frame + frame_size
                    start_time = start_frame / frame_rate
                    end_time = end_frame / frame_rate
                    silent_periods.append((start_time, end_time))
                    start_frame = frame_idx
                prev_frame = frame_idx
            
            end_frame = prev_frame + frame_size
            start_time = start_frame / frame_rate
            end_time = end_frame / frame_rate
            silent_periods.append((start_time, end_time))
            silent_periods_clustered = cluster(silent_periods)
        return silent_periods_clustered #type:ignore
    
    except wave.Error as e:
        raise ValueError(f"Cannot read WAV file: {e}")
    except Exception as e:
        raise Exception(f"Error occurred when processing: {e}")
    
if __name__ == '__main__':
    print(detect_no_sound_period('wav/0604.mp4_audio.wav'))