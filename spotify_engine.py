"""
Módulo nativo e robusto para download e conversão de músicas, álbuns e playlists do Spotify para MP3.
Extrai metadados oficiais diretamente da API de Embed do Spotify (sem necessidade de tokens ou credenciais)
e converte o áudio para MP3 em 320 kbps com tags ID3 (Título, Artista, Álbum, Capa) embutidas.
"""

import os
import sys
import re
import html
import json
import requests
import yt_dlp
import ffmpeg_utils
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, APIC, ID3NoHeaderError

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def clean_filename(name: str) -> str:
    """Remove caracteres inválidos para nomes de arquivos."""
    return re.sub(r'[\\/*?:"<>|]', '', name).strip()

def parse_spotify_url(url: str):
    """Extrai o tipo (track, album, playlist) e o ID de um link do Spotify."""
    match = re.search(r'(?:spotify\.com/(?:[a-zA-Z-]+/)?(track|album|playlist)/|spotify:(track|album|playlist):)([a-zA-Z0-9]+)', url)
    if match:
        kind = match.group(1) or match.group(2)
        item_id = match.group(3)
        return kind, item_id
    return None, None

def fetch_spotify_embed_data(kind: str, item_id: str) -> dict:
    """Obtém os dados estruturados da entidade a partir da página de embed do Spotify."""
    url = f"https://open.spotify.com/embed/{kind}/{item_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return None
        
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', resp.text)
        if not match:
            return None

        data = json.loads(match.group(1))
        entity = data.get("props", {}).get("pageProps", {}).get("state", {}).get("data", {}).get("entity", {})
        return entity
    except Exception as e:
        print(f"[Spotify] Erro ao consultar metadados: {e}", file=sys.stderr)
        return None

def extract_best_image_url(visual_identity) -> str:
    """Obtém a imagem de maior resolução disponível."""
    if not visual_identity or not isinstance(visual_identity, dict):
        return ""
    images = visual_identity.get("image", [])
    if isinstance(images, list) and images:
        # Pega a última ou a que tiver maior largura
        return images[-1].get("url", "")
    elif isinstance(images, dict):
        return images.get("url", "")
    return ""

def get_track_metadata(track_id: str) -> dict:
    """Obtém metadados completos de uma faixa."""
    entity = fetch_spotify_embed_data("track", track_id)
    if not entity:
        return None

    title = entity.get("title") or entity.get("name") or "Música Desconhecida"
    artists_list = entity.get("artists", [])
    if artists_list and isinstance(artists_list, list):
        artist = ", ".join([a.get("name", "") for a in artists_list if a.get("name")])
    else:
        artist = entity.get("subtitle", "")

    release_date = entity.get("releaseDate", {})
    year = ""
    if isinstance(release_date, dict):
        iso = release_date.get("isoString", "")
        if len(iso) >= 4:
            year = iso[:4]

    image_url = extract_best_image_url(entity.get("visualIdentity"))

    return {
        "title": title,
        "artist": artist,
        "album": "",
        "year": year,
        "image": image_url
    }

def get_container_tracks(kind: str, item_id: str) -> tuple:
    """Obtém lista de faixas de uma Playlist ou Álbum."""
    entity = fetch_spotify_embed_data(kind, item_id)
    if not entity:
        return "", []

    container_name = entity.get("title") or entity.get("name") or ("Álbum" if kind == "album" else "Playlist")
    image_url = extract_best_image_url(entity.get("visualIdentity"))
    raw_tracks = entity.get("trackList", [])

    tracks = []
    for t in raw_tracks:
        tracks.append({
            "title": t.get("title", ""),
            "artist": t.get("subtitle", ""),
            "album": container_name if kind == "album" else "",
            "year": "",
            "image": image_url
        })

    return container_name, tracks

def download_and_tag_track(track_info: dict, output_dir: str = "downloads", bitrate: str = "320") -> bool:
    """Busca o áudio correspondente no YouTube, converte para MP3 320k e embute metadados ID3."""
    os.makedirs(output_dir, exist_ok=True)
    title = track_info.get("title", "").strip()
    artist = track_info.get("artist", "").strip()
    album = track_info.get("album", "").strip()
    year = track_info.get("year", "").strip()
    image_url = track_info.get("image", "").strip()

    if not title:
        print("[Spotify] Erro: Título da música não informado.", file=sys.stderr)
        return False

    query = f"{artist} - {title}".strip(" -")
    print(f"\n[Spotify] Buscando áudio correspondente para: '{query}'...")

    filename_base = clean_filename(f"{artist} - {title}" if artist else title)
    expected_mp3 = os.path.join(output_dir, f"{filename_base}.mp3")

    # Opções do yt-dlp para extração e codificação em MP3 320k
    clean_bitrate = str(bitrate).replace("k", "")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, f"{filename_base}.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': clean_bitrate,
        }],
        'quiet': False,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch1:{query} audio"])
    except Exception as e:
        print(f"[Spotify] Falha ao baixar áudio: {e}", file=sys.stderr)
        return False

    # Identificar o arquivo MP3 resultante
    actual_mp3 = None
    if os.path.exists(expected_mp3):
        actual_mp3 = expected_mp3
    else:
        # Busca caso o yt-dlp tenha sanitizado o nome ligeiramente diferente
        candidates = [os.path.join(output_dir, f) for f in os.listdir(output_dir) 
                      if f.endswith(".mp3") and filename_base[:12].lower() in f.lower()]
        if candidates:
            actual_mp3 = candidates[0]

    if not actual_mp3 or not os.path.exists(actual_mp3):
        print(f"[Spotify] Erro: Arquivo MP3 não encontrado após conversão.", file=sys.stderr)
        return False

    # Inserir tags ID3 oficiais do Spotify
    print(f"[Spotify] Gravando tags ID3 oficiais (Título, Artista, Capa em alta resolução)...")
    try:
        try:
            audio = MP3(actual_mp3, ID3=ID3)
        except ID3NoHeaderError:
            audio = MP3(actual_mp3)
            audio.add_tags()

        if audio.tags is None:
            audio.add_tags()

        if title:
            audio.tags.add(TIT2(encoding=3, text=title))
        if artist:
            audio.tags.add(TPE1(encoding=3, text=artist))
        if album:
            audio.tags.add(TALB(encoding=3, text=album))
        if year:
            audio.tags.add(TDRC(encoding=3, text=str(year)))

        if image_url:
            try:
                img_data = requests.get(image_url, headers=HEADERS, timeout=10).content
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime='image/jpeg',
                        type=3,  # Capa Frontal
                        desc='Cover',
                        data=img_data
                    )
                )
            except Exception as e:
                print(f"[Spotify] Aviso: Não foi possível anexar a capa: {e}")

        audio.save()
        print(f"[Spotify] Sucesso! Música salva em: {os.path.abspath(actual_mp3)}")
        return True
    except Exception as e:
        print(f"[Spotify] Erro ao gravar tags ID3: {e}", file=sys.stderr)
        return False

def download_spotify(url: str, output_dir: str = "downloads", bitrate: str = "320") -> bool:
    """Ponto de entrada para qualquer link do Spotify (faixa, álbum ou playlist)."""
    kind, item_id = parse_spotify_url(url)
    if not kind or not item_id:
        print(f"[Spotify] Erro: Não foi possível reconhecer o link do Spotify: '{url}'", file=sys.stderr)
        return False

    if kind == "track":
        print(f"\n[Spotify] Obtendo metadados oficiais da faixa...")
        meta = get_track_metadata(item_id)
        if not meta or not meta.get("title"):
            print(f"[Spotify] Erro ao obter dados da faixa no Spotify.", file=sys.stderr)
            return False
        print(f"[Spotify] Faixa encontrada: '{meta.get('artist')} - {meta.get('title')}'")
        return download_and_tag_track(meta, output_dir=output_dir, bitrate=bitrate)

    elif kind in ("album", "playlist"):
        print(f"\n[Spotify] Analisando {kind}...")
        container_name, tracks = get_container_tracks(kind, item_id)
        if not tracks:
            print(f"[Spotify] Nenhuma faixa encontrada na {kind}.", file=sys.stderr)
            return False

        print(f"[Spotify] {kind.capitalize()}: '{container_name}' ({len(tracks)} faixas encontradas).")
        success = 0
        for i, t in enumerate(tracks, 1):
            print(f"\n[{i}/{len(tracks)}] Processando: {t.get('artist')} - {t.get('title')}")
            if download_and_tag_track(t, output_dir=output_dir, bitrate=bitrate):
                success += 1

        print(f"\n[Spotify] Concluído! {success}/{len(tracks)} faixas convertidas com sucesso.")
        return success > 0

    return False
