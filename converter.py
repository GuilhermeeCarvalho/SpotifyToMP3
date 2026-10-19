#!/usr/bin/env python3
"""
Music Converter — Conversor Inteligente de Músicas para MP3
Suporta:
- YouTube (Vídeos, Shorts, Playlists, YouTube Music ou busca por nome)
- Spotify (Músicas, Álbuns, Playlists)
- Arquivos de áudio locais (WAV, FLAC, M4A, OGG, AAC, etc.)
"""

import os
import sys
import argparse
from pathlib import Path

import ffmpeg_utils
from youtube_engine import download_youtube
from spotify_engine import download_spotify
from local_engine import convert_local_file, convert_local_directory, SUPPORTED_AUDIO_EXTENSIONS

DEFAULT_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")

def detect_and_process(target: str, output_dir: str = DEFAULT_OUTPUT, bitrate: str = "320"):
    target = target.strip().strip('"').strip("'")
    if not target:
        return

    # 1. Verificar se é caminho local
    local_path = Path(target)
    if local_path.is_file():
        convert_local_file(str(local_path), output_dir=output_dir, bitrate=bitrate)
        return
    elif local_path.is_dir():
        convert_local_directory(str(local_path), output_dir=output_dir, bitrate=bitrate)
        return

    # 2. Verificar se é Spotify
    if "spotify.com" in target or target.startswith("spotify:"):
        download_spotify(target, output_dir=output_dir, bitrate=bitrate)
        return

    # 3. Verificar se é YouTube
    if "youtube.com" in target or "youtu.be" in target:
        download_youtube(target, output_dir=output_dir, bitrate=bitrate)
        return

    # 4. Caso contrário, tratar como busca textual no YouTube
    print(f"\n[Busca] Termo detectado: '{target}'. Pesquisando áudio correspondente...")
    download_youtube(target, output_dir=output_dir, bitrate=bitrate)

def interactive_mode():
    print("=" * 60)
    print("       🎵 MUSIC CONVERTER — CONVERSOR DE MÚSICAS PARA MP3 🎵")
    print("=" * 60)
    print("Formatos aceitos:")
    print("  • Link do YouTube (vídeo, playlist ou YouTube Music)")
    print("  • Link do Spotify (música, álbum ou playlist)")
    print("  • Caminho de arquivo local (.wav, .flac, .m4a, etc.) ou pasta")
    print("  • Nome de música para buscar automaticamente (ex: 'Coldplay Yellow')")
    print("-" * 60)
    print(f"Diretório de saída: {DEFAULT_OUTPUT}")
    print("Qualidade de áudio padrão: 320 kbps (alta fidelidade)")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n👉 Cole o link, caminho ou nome da música (ou 'sair'): ").strip()
            if not user_input or user_input.lower() in ("sair", "exit", "quit", "q"):
                print("Encerrando. Até mais!")
                break
                
            detect_and_process(user_input, output_dir=DEFAULT_OUTPUT, bitrate="320")
            print("\n✔️ Processamento concluído!")
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada.")
            break

def main():
    parser = argparse.ArgumentParser(description="Conversor de Músicas e Vídeos para MP3 (YouTube, Spotify e Local)")
    parser.add_argument("target", nargs="?", help="Link do YouTube/Spotify, arquivo/pasta local ou termo de busca")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help="Diretório de saída para salvar os MP3s")
    parser.add_argument("-b", "--bitrate", default="320", help="Bitrate do MP3 em kbps (ex: 128, 192, 256, 320). Padrão: 320")
    
    args = parser.parse_args()
    
    if args.target:
        detect_and_process(args.target, output_dir=args.output, bitrate=args.bitrate)
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
