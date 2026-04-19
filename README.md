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
jarvis-pc/                      # Tous les fichiers à la racine
├── Ai engine.py                # Interface LLM modulaire
├── Audio engine.py             # Thread audio dédié, VAD, micro
├── Clap detector.py            # Détection double clap (RMS + transitoire)
├── Commander.py                # Exécution sécurisée de commandes
├── Config.py                   # Configuration centrale
├── Index.html                  # UI complète (shader WebGL + orb + visualiseur)
├── Main.js                     # Electron — fenêtre overlay, raccourci global
├── Main.py                     # Serveur WebSocket, orchestration
├── README.md                   # Ce fichier
├── Start.sh                    # Script de démarrage Linux/macOS
└── requirements.txt            # Dépendances Python
```

**Communication** : WebSocket local (`ws://localhost:8765/ws`) — bidirectionnel, faible latence, JSON.

> ⚠️ Les fichiers sont à la racine du repo. Les imports Python doivent donc utiliser les noms exacts tels qu’ils apparaissent sur GitHub (ex: `import Commander` et non `from core.commander import ...`).

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

### 1. Cloner le repo

```bash
git clone https://github.com/vous/jarvis-pc.git
cd jarvis-pc
```

### 2. Dépendances Python

```bash
pip install -r requirements.txt
```

> Pour utiliser Whisper avec GPU (optionnel, beaucoup plus rapide) :
> 
> ```bash
> pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
> ```

### 3. Dépendances Electron

```bash
npm install electron
```

-----

## Configuration

Tout se configure dans `Config.py`.

### Clé OpenAI (recommandé)

```bash
export OPENAI_API_KEY="sk-..."
```

### Mode offline (aucune API)

```python
# Dans Config.py
mode="offline"  # Matching par patterns locaux, aucune connexion requise
```

### Mode LLM local (Ollama)

```bash
# Installer Ollama : https://ollama.ai
ollama pull mistral
```

```python
# Dans Config.py
mode="local_llm"
local_llm_model="mistral"
```

### Sensibilité des claps

```python
# Dans Config.py
clap_threshold=0.35      # 0.1 = très sensible, 0.9 = peu sensible
clap_max_interval=0.6    # Secondes max entre les 2 claps
```

### Applications autorisées

```python
# Dans Config.py
allowed_apps=["chrome", "firefox", "code", "spotify", ...]
```

-----

## Lancement

### Interface complète (Electron)

```bash
chmod +x Start.sh
./Start.sh
```

### Test rapide dans le navigateur (sans Electron)

```bash
# Terminal 1 — Backend
python Main.py

# Terminal 2 — Ouvrir l'UI
open Index.html          # macOS
xdg-open Index.html      # Linux
start Index.html         # Windows
```

L’UI fonctionne en **mode démo** sans backend (animation WebGL + input texte, sans voix ni commandes système).

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

Tapez directement dans le champ en bas de l’interface — alternative si pas de micro.

### Simulation (sans micro)

Cliquez sur l’orbe central pour simuler un double clap.

-----

## Sécurité

- **Liste blanche** : seules les applications listées dans `Config.py` peuvent être lancées.
- **Accès fichiers restreint** : seuls les fichiers dans le dossier home (`~/`) sont accessibles.
- **Actions critiques** : `rm`, `shutdown`, `format` sont bloquées par défaut.
- **Journalisation** : toutes les actions sont écrites dans `jarvis.log`.
- **IPC sécurisé** : `contextIsolation: true` dans Electron.

-----

## Personnalisation

### Changer la personnalité

Dans `Config.py` :

```python
personality = """Tu es JARVIS, sarcastique mais efficace.
Tu réponds en une seule phrase. Tu appelles l'utilisateur "patron"."""
```

### Ajouter une commande

Dans `Ai engine.py`, section `OFFLINE_PATTERNS` :

```python
(r"(?:météo|temps qu'il fait)", "get_weather"),
```

Puis gérez l’action dans `Main.py`.

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

Vérifiez que votre micro est bien le périphérique par défaut.

**Whisper télécharge le modèle au premier lancement**
Normal. Le modèle `base` (~150 Mo) est téléchargé une seule fois dans `~/.cache/whisper/`.

**WebSocket ne se connecte pas**
Lancez d’abord `python Main.py`, puis ouvrez `Index.html`.

**Claps non détectés**
Diminuez `clap_threshold` dans `Config.py` (essayez `0.2`).

-----

## Roadmap

- [ ] Hotword personnalisé (“Hey Jarvis”) via Porcupine
- [ ] Plugin agenda (Google Calendar)
- [ ] Plugin domotique (Home Assistant)
- [ ] Mode multimodal (capture d’écran + analyse image)
- [ ] Build packagé (`.dmg` / `.exe` / `.AppImage`)

-----

## Licence

MIT — Libre d’utilisation, modification et distribution.
