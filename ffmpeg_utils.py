"""
Utilitário para detecção e configuração automática do FFmpeg no PATH.
"""

import os
import glob
import shutil

def setup_ffmpeg_path():
    """Garante que o FFmpeg e FFprobe estejam disponíveis no PATH do processo."""
    if shutil.which("ffmpeg"):
        return True
        
    candidates = glob.glob(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\*FFmpeg*\*\bin"))
    candidates += [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links"),
        r"C:\Program Files (x86)\Vcows",
        r"C:\Program Files\ffmpeg\bin",
        r"C:\ffmpeg\bin"
    ]
    
    for candidate in candidates:
        if os.path.exists(os.path.join(candidate, "ffmpeg.exe")):
            os.environ["PATH"] = candidate + os.pathsep + os.environ["PATH"]
            return True
            
    return False

# Executar automaticamente na importação
setup_ffmpeg_path()
