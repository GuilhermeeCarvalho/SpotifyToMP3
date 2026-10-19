"""
Módulo para download e conversão de áudio do YouTube / YouTube Music para MP3.
"""

import os
import sys
import yt_dlp
import ffmpeg_utils

def download_youtube(url_or_query: str, output_dir: str = "downloads", bitrate: str = "320") -> bool:
    """
    Baixa o melhor fluxo de áudio do YouTube e converte para MP3 em alta qualidade.
    Suporta links diretos de vídeo, playlist ou busca por texto.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Se for apenas texto de busca e não URL, adicionar prefixo de busca
    if not (url_or_query.startswith("http://") or url_or_query.startswith("https://")):
        target = f"ytsearch1:{url_or_query}"
    else:
        target = url_or_query
        
    outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'writethumbnail': True,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': bitrate,
            },
            {
                'key': 'EmbedThumbnail',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
        ],
        'quiet': False,
        'no_warnings': True,
    }
    
    print(f"\n[YouTube] Processando: {url_or_query}...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([target])
        print(f"[YouTube] Sucesso! Arquivo(s) salvo(s) em: {os.path.abspath(output_dir)}")
        return True
    except Exception as e:
        print(f"[YouTube] Erro ao converter: {e}", file=sys.stderr)
        return False
