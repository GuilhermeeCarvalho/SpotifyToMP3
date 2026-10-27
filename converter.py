#!/usr/bin/env python3
"""
Music Converter — Conversor Inteligente de Músicas para MP3
Suporta:
- YouTube (Vídeos, Shorts, Playlists, YouTube Music ou busca por nome)
- Spotify (Músicas, Álbuns, Playlists) com suporte a tags ID3 e fallback SoundCloud
- Arquivos de áudio locais (WAV, FLAC, M4A, OGG, AAC, etc.)
- Autenticação por cookies (cookies.txt) e JavaScript Runtime (Node.js)
"""

import os
import sys
import argparse
from pathlib import Path

import ffmpeg_utils
from ytdlp_utils import find_cookies_file
from youtube_engine import download_youtube
from spotify_engine import download_spotify
from local_engine import convert_local_file, convert_local_directory, SUPPORTED_AUDIO_EXTENSIONS

DEFAULT_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")

def detect_and_process(
    target: str, 
    output_dir: str = DEFAULT_OUTPUT, 
    bitrate: str = "320",
    cookies_file: str = None,
    cookies_browser: str = None
):
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
        download_spotify(
            target, 
            output_dir=output_dir, 
            bitrate=bitrate,
            cookies_file=cookies_file,
            cookies_browser=cookies_browser
        )
        return

    # 3. Verificar se é YouTube
    if "youtube.com" in target or "youtu.be" in target:
        download_youtube(
            target, 
            output_dir=output_dir, 
            bitrate=bitrate,
            cookies_file=cookies_file,
            cookies_browser=cookies_browser
        )
        return

    # 4. Caso contrário, tratar como busca textual
    print(f"\n[Busca] Termo detectado: '{target}'. Pesquisando áudio correspondente...")
    download_youtube(
        target, 
        output_dir=output_dir, 
        bitrate=bitrate,
        cookies_file=cookies_file,
        cookies_browser=cookies_browser
    )

def interactive_mode(cookies_file: str = None, cookies_browser: str = None):
    active_cookies = find_cookies_file(cookies_file)
    cookie_status = f"✅ Ativo ({os.path.basename(active_cookies)})" if active_cookies else "ℹ️ Não configurado (fallback ativo)"

    print("=" * 65)
    print("       🎵 MUSIC CONVERTER — CONVERSOR DE MÚSICAS PARA MP3 🎵")
    print("=" * 65)
    print("Formatos aceitos:")
    print("  • Link do YouTube (vídeo, playlist ou YouTube Music)")
    print("  • Link do Spotify (música, álbum ou playlist)")
    print("  • Caminho de arquivo local (.wav, .flac, .m4a, etc.) ou pasta")
    print("  • Nome de música para buscar automaticamente (ex: 'Coldplay Yellow')")
    print("-" * 65)
    print(f"Diretório de saída: {DEFAULT_OUTPUT}")
    print(f"Qualidade de áudio padrão: 320 kbps (alta fidelidade)")
    print(f"Status de Cookies do YouTube: {cookie_status}")
    print("=" * 65)
    
    while True:
        try:
            user_input = input("\n👉 Cole o link, caminho ou nome da música (ou 'sair'): ").strip()
            if not user_input or user_input.lower() in ("sair", "exit", "quit", "q"):
                print("Encerrando. Até mais!")
                break
                
            detect_and_process(
                user_input, 
                output_dir=DEFAULT_OUTPUT, 
                bitrate="320",
                cookies_file=cookies_file,
                cookies_browser=cookies_browser
            )
            print("\n✔️ Processamento concluído!")
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada.")
            break

def main():
    parser = argparse.ArgumentParser(description="Conversor de Músicas e Vídeos para MP3 (YouTube, Spotify e Local)")
    parser.add_argument("target", nargs="?", help="Link do YouTube/Spotify, arquivo/pasta local ou termo de busca")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT, help="Diretório de saída para salvar os MP3s")
    parser.add_argument("-b", "--bitrate", default="320", help="Bitrate do MP3 em kbps (ex: 128, 192, 256, 320). Padrão: 320")
    parser.add_argument("-c", "--cookies", default=None, help="Caminho para arquivo cookies.txt do YouTube")
    parser.add_argument("--cookies-from-browser", default=None, help="Navegador para importar cookies (ex: chrome, edge, firefox)")
    
    args = parser.parse_args()
    
    if args.target:
        detect_and_process(
            args.target, 
            output_dir=args.output, 
            bitrate=args.bitrate,
            cookies_file=args.cookies,
            cookies_browser=args.cookies_from_browser
        )
    else:
        interactive_mode(cookies_file=args.cookies, cookies_browser=args.cookies_from_browser)

if __name__ == "__main__":
    main()
