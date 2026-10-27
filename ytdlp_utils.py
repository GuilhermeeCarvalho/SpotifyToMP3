"""
Utilitários de configuração do yt-dlp:
- Detecção e uso automático de cookies (cookies.txt ou cookies-from-browser)
- Configuração do runtime JavaScript (Node.js) para resolução de desafios EJS
- Opções base padronizadas para extração de áudio e conversão para MP3
"""

import os
import sys
import shutil

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def find_cookies_file(custom_path: str = None) -> str:
    """Busca um arquivo cookies.txt existente no projeto ou diretório atual."""
    if custom_path and os.path.isfile(custom_path):
        return os.path.abspath(custom_path)

    candidates = [
        os.path.join(PROJECT_DIR, "cookies.txt"),
        os.path.join(PROJECT_DIR, "youtube_cookies.txt"),
        os.path.join(PROJECT_DIR, "youtube.com_cookies.txt"),
        os.path.join(os.getcwd(), "cookies.txt"),
        os.path.expanduser("~/cookies.txt"),
    ]
    for c in candidates:
        if os.path.isfile(c) and os.path.getsize(c) > 0:
            return os.path.abspath(c)
    return None

def get_ytdlp_options(
    outtmpl: str,
    bitrate: str = "320",
    embed_thumbnail: bool = False,
    add_metadata: bool = False,
    cookies_file: str = None,
    cookies_browser: str = None
) -> dict:
    """Retorna as opções otimizadas do yt-dlp com tratamento de cookies e JS runtime."""
    clean_bitrate = str(bitrate).replace("k", "")

    postprocessors = [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': clean_bitrate,
        }
    ]
    if embed_thumbnail:
        postprocessors.append({'key': 'EmbedThumbnail'})
    if add_metadata:
        postprocessors.append({'key': 'FFmpegMetadata', 'add_metadata': True})

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': outtmpl,
        'postprocessors': postprocessors,
        'writethumbnail': embed_thumbnail,
        'quiet': False,
        'no_warnings': True,
        'sleep_interval': 1,
        'max_sleep_interval': 2,
    }

    # Ativar Node.js como JavaScript Runtime se instalado (necessário para PoToken do YouTube)
    if shutil.which("node"):
        ydl_opts['js_runtimes'] = {'node': {}}

    # Detecção e aplicação de cookies
    active_cookie = find_cookies_file(cookies_file)
    if active_cookie:
        ydl_opts['cookiefile'] = active_cookie
        print(f"[Cookies] Usando arquivo de cookies: {active_cookie}")
    elif cookies_browser:
        ydl_opts['cookiesfrombrowser'] = (cookies_browser,)
        print(f"[Cookies] Carregando cookies do navegador: {cookies_browser}")

    return ydl_opts

def is_bot_or_cookie_error(err_str: str) -> bool:
    """Verifica se a mensagem de erro é o bloqueio de bot/cookies do YouTube."""
    keywords = [
        "confirm you’re not a bot",
        "confirm you're not a bot",
        "sign in to confirm",
        "bot detection",
        "use --cookies-from-browser",
        "use --cookies"
    ]
    err_lower = err_str.lower()
    return any(k in err_lower for k in keywords)

def print_cookie_help():
    """Exibe instruções claras e passo a passo de como resolver o erro de cookies."""
    print("\n" + "=" * 65)
    print("⚠️  BLOQUEIO DE BOT DO YOUTUBE DETECTADO")
    print("=" * 65)
    print("O YouTube sinalizou as requisições recentes como tráfego automatizado.")
    print("Para resolver de forma definitiva em downloads diretos do YouTube:")
    print(" 1. No seu navegador (Chrome ou Edge), instale a extensão")
    print("    'Get cookies.txt LOCALLY'.")
    print(" 2. Acesse o YouTube (logado na sua conta Google) e clique na extensão.")
    print(" 3. Clique no botão de exportar/baixar o arquivo 'cookies.txt'.")
    print(f" 4. Mova o arquivo 'cookies.txt' para a pasta deste projeto:")
    print(f"    📂 {PROJECT_DIR}")
    print("O conversor reconhecerá o arquivo automaticamente a partir de agora!")
    print("=" * 65 + "\n")
