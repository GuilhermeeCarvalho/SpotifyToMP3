"""
Módulo para conversão de arquivos de áudio locais (WAV, FLAC, M4A, OGG, AAC, etc.) para MP3.
Utiliza o FFmpeg com o codec libmp3lame em alta qualidade.
"""

import os
import sys
import subprocess
from pathlib import Path
import ffmpeg_utils

SUPPORTED_AUDIO_EXTENSIONS = {
    ".wav", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".wma", ".aiff", ".alac", ".webm", ".mkv", ".mp4"
}

def convert_local_file(input_path: str, output_dir: str = "downloads", bitrate: str = "320k") -> bool:
    """
    Converte um único arquivo de áudio local para MP3.
    """
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"[Local] Erro: Arquivo '{input_path}' não encontrado.", file=sys.stderr)
        return False
        
    os.makedirs(output_dir, exist_ok=True)
    output_file = Path(output_dir) / f"{input_file.stem}.mp3"
    
    clean_bitrate = f"{bitrate}k" if not str(bitrate).endswith("k") else str(bitrate)
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_file),
        "-vn",
        "-codec:a", "libmp3lame",
        "-b:a", clean_bitrate,
        str(output_file)
    ]
    
    print(f"\n[Local] Convertendo '{input_file.name}' -> '{output_file.name}'...")
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print(f"[Local] Concluído com sucesso! Salvo em: {output_file.resolve()}")
            return True
        else:
            print(f"[Local] Erro no FFmpeg: {res.stderr}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"[Local] Falha na execução do FFmpeg: {e}", file=sys.stderr)
        return False

def convert_local_directory(input_dir: str, output_dir: str = "downloads", bitrate: str = "320k") -> int:
    """
    Varre um diretório local e converte todos os arquivos de áudio suportados para MP3.
    """
    p = Path(input_dir)
    if not p.is_dir():
        print(f"[Local] Erro: '{input_dir}' não é um diretório válido.", file=sys.stderr)
        return 0
        
    audio_files = [f for f in p.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS]
    if not audio_files:
        print(f"[Local] Nenhum arquivo de áudio suportado encontrado em: {input_dir}")
        return 0
        
    print(f"\n[Local] Encontrados {len(audio_files)} arquivos para converter em '{input_dir}'.")
    success_count = 0
    for f in audio_files:
        if convert_local_file(str(f), output_dir=output_dir, bitrate=bitrate):
            success_count += 1
            
    print(f"\n[Local] Finalizado: {success_count}/{len(audio_files)} convertidos com sucesso.")
    return success_count
