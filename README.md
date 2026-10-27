# 🎵 Music Converter (Python MP3 Suite)

Um conversor completo e inteligente de músicas e áudios para **MP3 em alta qualidade (320 kbps)**, com suporte a **YouTube**, **Spotify** (faixas, álbuns e playlists completas) e **arquivos de áudio locais**.

O projeto conta com gravação automática de metadados oficiais **ID3v2** (Título, Artistas, Álbum, Ano e Capa oficial do álbum embutida no arquivo MP3).

---

## ⚡ Recursos Principais

- 🎧 **YouTube & YouTube Music:** Baixe qualquer vídeo, Shorts ou playlist diretamente em MP3 320 kbps (com suporte a autenticação por `cookies.txt`).
- 🟢 **Spotify (Faixas, Álbuns e Playlists):** Extrai os metadados oficiais e converte para MP3 em alta fidelidade com capa oficial embutida. Conta com **fallback automático resiliente (SoundCloud)** caso o YouTube imponha restrição contra bots/cookies.
- 🔍 **Busca por Nome:** Digite apenas o nome da música e o artista (ex: `Coldplay - Yellow`) para buscar e converter automaticamente.
- 📁 **Conversão Local em Lote:** Converte arquivos de áudio locais (`.wav`, `.flac`, `.m4a`, `.aac`, `.ogg`, `.opus`, etc.) individuais ou pastas inteiras para MP3.
- 🏷️ **Tags ID3 Completas:** Título, Artista, Álbum, Ano e Imagem da Capa frontal (Cover Art) são embutidos diretamente no arquivo.
- 💻 **Multiplataforma:** Compatível com Windows, Linux e macOS.

---

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de ter instalado em seu computador:

1. **Python 3.10 ou superior:**
   - Verifique com: `python --version`
   - Download oficial: [python.org](https://www.python.org/) (no Windows, marque a opção **"Add Python to PATH"** durante a instalação).

2. **FFmpeg:**
   - O FFmpeg é o motor responsável pela codificação do áudio para MP3.
   - **Windows (via winget):**
     ```powershell
     winget install Gyan.FFmpeg.Essentials
     ```
   - **Linux (Ubuntu/Debian):**
     ```bash
     sudo apt update && sudo apt install ffmpeg
     ```
   - **macOS (via Homebrew):**
     ```bash
     brew install ffmpeg
     ```

---

## 🚀 Passo a Passo: Instalação e Execução do Zero

### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/music-converter.git
cd music-converter
```

### 2. (Opcional, mas recomendado) Criar e ativar um ambiente virtual

* **No Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **No Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar as dependências do projeto
```bash
pip install -r requirements.txt
```

---

## 🎮 Como Usar

### Modo 1: Interativo (Mais Fácil)
Inicie o programa sem parâmetros para abrir o menu interativo:
```bash
python converter.py
```
Você verá o prompt:
```text
============================================================
       🎵 MUSIC CONVERTER — CONVERSOR DE MÚSICAS PARA MP3 🎵
============================================================
👉 Cole o link, caminho ou nome da música (ou 'sair'): 
```
Basta colar qualquer link do YouTube, Spotify, caminho de pasta/arquivo ou digitar o nome de uma música.

---

### Modo 2: Linha de Comando (Direto)

#### 🟢 Spotify (Música Individual, Álbum ou Playlist)
```bash
# Faixa individual:
python converter.py "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"

# Playlist inteira:
python converter.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

# Álbum completo:
python converter.py "https://open.spotify.com/album/4m2880jivSbbyEGAKfITCa"
```

#### ▶️ YouTube / YouTube Music
```bash
# Vídeo ou música individual:
python converter.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Playlist do YouTube:
python converter.py "https://www.youtube.com/playlist?list=PLrEnWoR732-BHrPp_Pm8_VleD68f9n14-"
```

#### 🔍 Busca por Nome de Música
```bash
python converter.py "Rick Astley Never Gonna Give You Up"
```

#### 📁 Arquivos Locais (FLAC, WAV, M4A, etc.)
```bash
# Arquivo único:
python converter.py "C:\Users\Nome\Music\audio.flac"

# Pasta inteira (conversão em lote):
python converter.py "C:\Users\Nome\Music\MinhaPastaSemMP3"
```

---

## ⚙️ Opções Avançadas

| Parâmetro | Descrição | Padrão |
| :--- | :--- | :--- |
| `-o`, `--output` | Diretório de destino para salvar os arquivos MP3 | `downloads/` |
| `-b`, `--bitrate` | Taxa de bits do MP3 (ex: `128`, `192`, `256`, `320`) | `320` (kbps) |

**Exemplo:**
```bash
python converter.py "https://open.spotify.com/track/..." -o "D:\Musicas" -b 256
```

---

##
 🍪 Solução para Bloqueio de Cookies do YouTube ("Sign in to confirm you're not a bot")

O YouTube frequentemente impõe verificações contra bots quando muitas músicas são baixadas seguidas. O projeto já inclui duas proteções automáticas:

1. **Fallback Automático (Spotify e buscas de áudio):** Se o YouTube bloquear o acesso, o conversor busca automaticamente a faixa no SoundCloud em alta fidelidade e preserva as capas e tags oficiais do Spotify!

## Adicione seus prpios cookies
2. **Suporte a `cookies.txt` (Para downloads diretos do YouTube):**
   - Instale a extensão de navegador [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) (disponível para Chrome, Edge e Firefox).
   - Entre no YouTube com sua conta logada.
   - Abra a extensão e clique em **Export**.
   - Salve o arquivo como `cookies.txt` na pasta raiz deste projeto:
     ```text
     SpotifyToMP3/cookies.txt
     ```
   - O conversor detectará o arquivo automaticamente ao ser iniciado!

---

## 📂 Estrutura do Projeto

```text
music-converter/
├── converter.py          # Ponto de entrada (CLI e modo interativo)
├── spotify_engine.py     # Motor nativo de resolução e tags do Spotify
├── youtube_engine.py     # Motor de download e conversão do YouTube
├── local_engine.py       # Conversor em lote para arquivos locais
├── ffmpeg_utils.py       # Detecção automática do FFmpeg no sistema
├── requirements.txt      # Dependências Python (yt-dlp, mutagen, requests)
├── .gitignore            # Arquivos ignorados pelo Git
├── README.md             # Esta documentação
└── downloads/            # Pasta padrão onde os MP3s são salvos
```

---

