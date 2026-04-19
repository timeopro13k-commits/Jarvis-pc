# JARVIS — Assistant IA Desktop

> *“Bienvenue, monsieur. Tous les systèmes sont opérationnels.”*

Interface futuriste inspirée de Jarvis, activable par double claquement de mains, avec commandes vocales, animation WebGL temps réel et exécution sécurisée de commandes système.

-----

## Aperçu

JARVIS est un assistant desktop qui tourne en arrière-plan et se réveille sur un **double clap**. Il écoute vos commandes vocales, interagit avec un LLM (OpenAI ou local), et peut lancer des applications, obtenir des infos système, ouvrir des fichiers — le tout derrière une interface HUD futuriste animée en WebGL.

```
Double clap → Activation → Commande vocale → Action système + Réponse IA
```

-----

## Fonctionnalités

|Fonctionnalité      |Détail                                                                     |
|--------------------|---------------------------------------------------------------------------|
|👏 Détection de claps|Algorithme RMS + transitoire, calibration adaptative au bruit ambiant      |
|🎙️ STT               |Whisper (offline) — modèles `tiny` à `medium`                              |
|🔊 TTS               |pyttsx3 (offline, cross-platform)                                          |
|🧠 IA                |OpenAI GPT-4o-mini, Ollama (local), ou fallback offline par patterns       |
|🖥️ UI                |Overlay Electron transparent, toujours au premier plan                     |
|🌊 Animation         |Shader GLSL — vague de carrés depuis le centre, réactif au niveau audio    |
|⚙️ Commandes         |Lancement d’apps, infos système, ouverture de fichiers                     |
|🔐 Sécurité          |Liste blanche, sandbox, journalisation, confirmation pour actions critiques|
|⌨️ Mode texte        |Input clavier en alternative à la voix                                     |

-----

## Architecture

```
jarvis/
├── backend/                    # Python — FastAPI + asyncio
│   ├── main.py                 # Serveur WebSocket, orchestration
│   ├── config.py               # Configuration centrale
│   └── core/
│       ├── clap_detector.py    # Détection double clap (RMS + transitoire)
│       ├── audio_engine.py     # Thread audio dédié, VAD, micro
│       ├── ai_engine.py        # Interface LLM modulaire
│       └── commander.py        # Exécution sécurisée de commandes
│
├── frontend/                   # HTML + WebGL GLSL
│   └── index.html              # UI complète (shader + orb + visualiseur)
│
└── electron/                   # Wrapper desktop
    ├── main.js                 # Fenêtre overlay, tray, raccourci global
    ├── preload.js              # Bridge sécurisé renderer/main
    └── package.json
```

**Communication** : WebSocket local (`ws://localhost:8765/ws`) — bidirectionnel, faible latence, JSON.

-----

## Prérequis

- **Python** 3.10+
- **Node.js** 18+ (pour Electron)
- **ffmpeg** (requis par Whisper pour le STT)
- Microphone fonctionnel

Installation de ffmpeg :

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows
winget install ffmpeg
```

-----

## Installation

### 1. Cloner et préparer

```bash
git clone https://github.com/vous/jarvis.git
cd jarvis
```

### 2. Backend Python

```bash
pip install -r requirements.txt
```

> Pour utiliser Whisper avec GPU (optionnel, beaucoup plus rapide) :
> 
> ```bash
> pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
> ```

### 3. Frontend Electron

```bash
cd electron
npm install
cd ..
```

-----

## Configuration

Tout se configure dans `backend/config.py`.

### Clé OpenAI (recommandé)

```bash
export OPENAI_API_KEY="sk-..."
```

Ou directement dans `config.py` :

```python
ai: AIConfig = field(default_factory=lambda: AIConfig(
    mode="openai",
    openai_api_key="sk-..."
))
```

### Mode offline (aucune API)

```python
ai: AIConfig = field(default_factory=lambda: AIConfig(
    mode="offline"  # Matching par patterns locaux
))
```

### Mode LLM local (Ollama)

```bash
# Installer Ollama : https://ollama.ai
ollama pull mistral
```

```python
ai: AIConfig = field(default_factory=lambda: AIConfig(
    mode="local_llm",
    local_llm_model="mistral"
))
```

### Sensibilité de détection des claps

```python
audio: AudioConfig = field(default_factory=lambda: AudioConfig(
    clap_threshold=0.35,      # 0.1 = très sensible, 0.9 = peu sensible
    clap_max_interval=0.6,    # Secondes max entre les 2 claps
))
```

### Applications autorisées

```python
security: SecurityConfig = field(default_factory=lambda: SecurityConfig(
    allowed_apps=["chrome", "firefox", "code", "spotify", ...]
))
```

-----

## Lancement

### Interface complète (Electron + Backend)

```bash
chmod +x start.sh
./start.sh
```

### Test rapide sans Electron (navigateur)

```bash
# Terminal 1 — Backend
cd backend && python main.py

# Terminal 2 — Ouvrir l'UI dans le navigateur
open frontend/index.html
```

L’UI fonctionne en **mode démo** sans backend (animation WebGL + input texte, sans voix ni commandes système).

### Backend seul (debug)

```bash
cd backend && python main.py
```

### Raccourci global

`Ctrl + Shift + J` (Windows/Linux) ou `Cmd + Shift + J` (macOS) pour afficher/masquer la fenêtre.

-----

## Utilisation

### Activation par double clap

Claquez des mains deux fois rapidement (intervalle 0.1–0.6 sec). L’orbe passe au vert et JARVIS entre en mode écoute.

### Commandes vocales (exemples)

```
"Ouvre Chrome"
"Lance VS Code"
"Quelle heure est-il ?"
"Infos système"
"Ouvre le fichier rapport.pdf"
"Au revoir"
```

### Input texte

Tapez directement dans le champ en bas de l’interface.

### Simulation (sans micro)

Cliquez sur l’orbe central pour simuler un double clap.

-----

## Sécurité

- **Liste blanche** : seules les applications explicitement listées dans `allowed_apps` peuvent être lancées.
- **Accès fichiers restreint** : seuls les fichiers dans le dossier home (`~/`) sont accessibles.
- **Actions critiques** : les commandes comme `rm`, `shutdown`, `format` sont bloquées par défaut et nécessitent une confirmation explicite.
- **Journalisation** : toutes les actions sont écrites dans `jarvis.log`.
- **Pas d’accès réseau** depuis les commandes utilisateur.
- **IPC sécurisé** : `contextIsolation: true` dans Electron, API minimale exposée via `preload.js`.

-----

## Personnalisation

### Changer la personnalité

Dans `config.py`, modifiez `personality` :

```python
personality: str = """Tu es JARVIS, un assistant sarcastique mais redoutablement efficace.
Tu réponds toujours en une seule phrase incisive.
Tu appelles l'utilisateur "patron"."""
```

### Ajouter un plugin

Créez `backend/plugins/mon_plugin.py` :

```python
class MonPlugin:
    name = "mon_plugin"
    
    async def execute(self, intent, commander) -> str:
        if "météo" in intent.target:
            # votre logique
            return "Il fait beau."
        return None
```

Enregistrez-le dans `main.py` :

```python
from plugins.mon_plugin import MonPlugin
plugins = [MonPlugin()]
```

-----

## Dépendances principales

|Package              |Rôle                            |
|---------------------|--------------------------------|
|`fastapi` + `uvicorn`|Serveur async + WebSocket       |
|`sounddevice`        |Capture microphone temps réel   |
|`numpy`              |Traitement signal audio         |
|`openai-whisper`     |STT offline                     |
|`pyttsx3`            |TTS offline                     |
|`httpx`              |Requêtes HTTP async (OpenAI API)|
|`psutil`             |Métriques système               |
|`electron`           |Fenêtre overlay desktop         |

-----

## Problèmes courants

**`sounddevice` ne trouve pas de micro**

```bash
python -c "import sounddevice; print(sounddevice.query_devices())"
```

Vérifiez que votre micro est bien sélectionné comme périphérique par défaut.

**Whisper télécharge le modèle au premier lancement**
C’est normal. Le modèle `base` (~150 Mo) est téléchargé une seule fois dans `~/.cache/whisper/`.

**WebSocket ne se connecte pas**
Vérifiez que le backend tourne bien (`python backend/main.py`) avant de lancer l’UI.

**Claps non détectés**
Diminuez `clap_threshold` dans `config.py` (essayez `0.2`). Évitez les environnements très brueux.

-----

## Roadmap

- [ ] Hotword personnalisé (“Hey Jarvis”) via Porcupine
- [ ] Plugin agenda (Google Calendar)
- [ ] Plugin domotique (Home Assistant)
- [ ] Mode multimodal (analyse d’image via capture d’écran)
- [ ] Mémorisation des préférences utilisateur
- [ ] Build Electron packagé (`.dmg` / `.exe` / `.AppImage`)

-----

## Licence

MIT — Libre d’utilisation, modification et distribution.
