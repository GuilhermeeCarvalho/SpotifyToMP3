"""
Módulo para download e conversão de áudio do YouTube / YouTube Music para MP3.
"""

import os
import sys
import yt_dlp
import ffmpeg_utils
from ytdlp_utils import get_ytdlp_options, is_bot_or_cookie_error, print_cookie_help

def download_youtube(
    url_or_query: str, 
    output_dir: str = "downloads", 
    bitrate: str = "320",
    cookies_file: str = None,
    cookies_browser: str = None
) -> bool:
    """
    Baixa o melhor fluxo de áudio do YouTube e converte para MP3 em alta qualidade.
    Suporta links diretos de vídeo, playlist ou busca por texto.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    is_url = url_or_query.startswith("http://") or url_or_query.startswith("https://")
    if not is_url:
        target = f"ytsearch1:{url_or_query}"
    else:
        target = url_or_query
        
    outtmpl = os.path.join(output_dir, "%(title)s.%(ext)s")
    
    ydl_opts = get_ytdlp_options(
        outtmpl=outtmpl,
        bitrate=bitrate,
        embed_thumbnail=True,
        add_metadata=True,
        cookies_file=cookies_file,
        cookies_browser=cookies_browser
    )
    
    print(f"\n[YouTube] Processando: {url_or_query}...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([target])
        print(f"[YouTube] Sucesso! Arquivo(s) salvo(s) em: {os.path.abspath(output_dir)}")
        return True
    except Exception as e:
        err_str = str(e)
        print(f"[YouTube] Erro ao converter: {e}", file=sys.stderr)
        
        # Se for busca por texto e falhar por bot, tenta fallback via SoundCloud
        if not is_url and is_bot_or_cookie_error(err_str):
            print(f"[Aviso] Tentando busca alternativa via SoundCloud para: '{url_or_query}'...")
            try:
                sc_opts = dict(ydl_opts)
                sc_opts.pop('cookiefile', None)
                sc_opts.pop('cookiesfrombrowser', None)
                with yt_dlp.YoutubeDL(sc_opts) as sc_ydl:
                    sc_ydl.download([f"scsearch1:{url_or_query}"])
                print(f"[SoundCloud] Sucesso! Arquivo(s) salvo(s) em: {os.path.abspath(output_dir)}")
                return True
            except Exception as sc_err:
                print(f"[SoundCloud] Erro no fallback: {sc_err}", file=sys.stderr)

        if is_bot_or_cookie_error(err_str):
            print_cookie_help()
            
        return False
