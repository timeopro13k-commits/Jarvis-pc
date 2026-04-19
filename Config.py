# Config.py

“””
Configuration centrale de JARVIS — Mode 100% offline, aucune clé requise.
“””

import os
from dataclasses import dataclass, field
from typing import List

@dataclass
class AudioConfig:
sample_rate: int = 44100
channels: int = 1
chunk_size: int = 1024
clap_threshold: float = 0.35
clap_min_interval: float = 0.1
clap_max_interval: float = 0.6
clap_cooldown: float = 1.5

@dataclass
class AIConfig:
# ✅ MODE OFFLINE TOTAL — aucune clé, aucune connexion
# “offline”   → réponses par patterns locaux (léger, instantané)
# “local_llm” → Ollama en local (plus intelligent, nécessite Ollama installé)
mode: str = “offline”

```
# Si vous installez Ollama (https://ollama.ai) :
# 1. Changez mode = "local_llm"
# 2. Lancez : ollama pull mistral
local_llm_url: str = "http://localhost:11434/api/generate"
local_llm_model: str = "mistral"

personality: str = """Tu es JARVIS, un assistant IA sophistiqué et élégant.
```

Tu es direct, efficace, légèrement sarcastique mais toujours serviable.
Tu réponds en français. Tes réponses sont concises (max 2-3 phrases).”””
max_tokens: int = 300

@dataclass
class SpeechConfig:
stt_engine: str = “whisper”
whisper_model: str = “base”
tts_engine: str = “pyttsx3”
tts_rate: int = 175
tts_volume: float = 0.9
voice_language: str = “fr”

@dataclass
class SecurityConfig:
allowed_commands: List[str] = field(default_factory=lambda: [
“open”, “start”, “xdg-open”,
“ls”, “dir”, “pwd”,
“echo”, “date”, “time”,
“python”, “node”,
])
allowed_apps: List[str] = field(default_factory=lambda: [
“chrome”, “firefox”, “safari”, “edge”,
“code”, “vscode”,
“terminal”, “cmd”, “powershell”,
“finder”, “explorer”,
“spotify”, “vlc”,
“calculator”, “notepad”,
])
require_confirmation: List[str] = field(default_factory=lambda: [
“rm”, “del”, “format”, “shutdown”, “reboot”,
“kill”, “taskkill”,
])
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
name: str = “JARVIS”
hotword: str = “jarvis”
debug: bool = False

CONFIG = JarvisConfig()
