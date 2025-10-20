import argparse
import logging
from .single_video_translation import VideoTranslator, Device

def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Transcribe and burn subtitles.")
    parser.add_argument("input", help="Path to input video")
    parser.add_argument("--model", default="large-v3", help="Model size")
    parser.add_argument("--device", default="cpu", help="Device: cpu or cuda")
    args = parser.parse_args()
    vt = VideoTranslator(args.input, args.model, device=Device(args.device))
    vt.singleVideoPipeline()

if __name__ == "__main__":
    main()
