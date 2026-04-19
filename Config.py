# backend/config.py

“””
Configuration centrale de JARVIS.
Modifier ce fichier pour personnaliser le comportement.
“””

import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class AudioConfig:
sample_rate: int = 44100
channels: int = 1
chunk_size: int = 1024
# Détection de claps
clap_threshold: float = 0.35       # Sensibilité (0.1 = très sensible, 0.9 = peu sensible)
clap_min_interval: float = 0.1     # Secondes min entre 2 claps
clap_max_interval: float = 0.6     # Secondes max entre 2 claps (double clap)
clap_cooldown: float = 1.5         # Pause après détection pour éviter les faux positifs

@dataclass
class AIConfig:
# Mode: “openai” | “offline” | “local_llm”
mode: str = “openai”
openai_api_key: str = os.getenv(“OPENAI_API_KEY”, “”)
model: str = “gpt-4o-mini”
# URL pour LLM local (ex: Ollama)
local_llm_url: str = “http://localhost:11434/api/generate”
local_llm_model: str = “mistral”
# Personnalité
personality: str = “”“Tu es JARVIS, un assistant IA sophistiqué et élégant.
Tu es direct, efficace, légèrement sarcastique mais toujours serviable.
Tu réponds en français par défaut. Tes réponses sont concises (max 2-3 phrases).
Tu peux exécuter des commandes système, lancer des applications et aider l’utilisateur.”””
max_tokens: int = 300

@dataclass
class SpeechConfig:
# STT: “whisper” | “google” | “vosk”
stt_engine: str = “whisper”
whisper_model: str = “base”  # tiny, base, small, medium
# TTS: “pyttsx3” | “gtts” | “elevenlabs”
tts_engine: str = “pyttsx3”
tts_rate: int = 175           # Vitesse de parole
tts_volume: float = 0.9
voice_language: str = “fr”

@dataclass
class SecurityConfig:
# Commandes système explicitement autorisées
allowed_commands: List[str] = field(default_factory=lambda: [
“open”, “start”, “xdg-open”,  # Lancer apps
“ls”, “dir”, “pwd”,            # Navigation
“echo”, “date”, “time”,        # Infos basiques
“python”, “node”,              # Interpréteurs
])
# Applications explicitement autorisées
allowed_apps: List[str] = field(default_factory=lambda: [
“chrome”, “firefox”, “safari”, “edge”,
“code”, “vscode”,
“terminal”, “cmd”, “powershell”,
“finder”, “explorer”,
“spotify”, “vlc”,
“calculator”, “notepad”,
])
# Actions nécessitant confirmation explicite
require_confirmation: List[str] = field(default_factory=lambda: [
“rm”, “del”, “format”, “shutdown”, “reboot”,
“kill”, “taskkill”,
])
# Journalisation
log_file: str = “jarvis_actions.log”
log_level: str = “INFO”

@dataclass
class ServerConfig:
host: str = “localhost”
port: int = 8765
ws_path: str = “/ws”

@dataclass
class JarvisConfig:
audio: AudioConfig = field(default_factory=AudioConfig)
ai: AIConfig = field(default_factory=AIConfig)
speech: SpeechConfig = field(default_factory=SpeechConfig)
security: SecurityConfig = field(default_factory=SecurityConfig)
server: ServerConfig = field(default_factory=ServerConfig)

```
# Nom de l'assistant
name: str = "JARVIS"
# Activation par mot-clé (en plus des claps)
hotword: str = "jarvis"
# Mode debug
debug: bool = False
```

# Instance globale

CONFIG = JarvisConfig()
