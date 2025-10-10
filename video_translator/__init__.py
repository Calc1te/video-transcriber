"""
video_translator - automatically generate transcription and compress subtitle with video
Translator haven't been implemented yet
"""

__version__ = "0.1.0"
__author__ = "Calc1te"

from .single_video_translation import VideoTranslator, Device
from .ass_subtitle_generator import AssStyle, AssGenerator

__all__ = [
    "VideoTranslator",
    "Device",
    "AssStyle",
    "AssGenerator",
]
