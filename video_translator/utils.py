from dataclasses import dataclass
@dataclass
class Transcription:
    start : str
    end : str
    text : str
def second_to_HMS(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        cs = int(round((seconds - int(seconds)) * 100))

        if cs == 100:
            cs = 0
            s += 1
            if s == 60:
                s = 0
                m += 1
                if m == 60:
                    m = 0
                    h += 1

        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"