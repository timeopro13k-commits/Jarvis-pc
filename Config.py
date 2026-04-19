# Config.py

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
clap_threshold: float = 0.35       # Sensibilité (0.1 = très sensible, 0.9 = peu sensible)
clap_min_interval: float = 0.1     # Secondes min entre 2 claps
clap_max_interval: float = 0.6     # Secondes max entre 2 claps
clap_cooldown: float = 1.5         # Pause après détection

@dataclass
class AIConfig:
# ✅ MODE OPENROUTER (gratuit, sans carte bancaire)
# Créez votre clé sur : https://openrouter.ai → Sign in → Keys → Create Key
mode: str = “openrouter”
openrouter_api_key: str = os.getenv(“OPENROUTER_API_KEY”, “COLLEZ_VOTRE_CLÉ_ICI”)

```
# Modèle gratuit à utiliser (tous gratuits sur OpenRouter avec :free)
# Options recommandées :
#   "meta-llama/llama-4-scout:free"     → Llama 4 (très bon)
#   "mistralai/mistral-7b-instruct:free" → Mistral 7B (léger)
#   "google/gemma-3-12b-it:free"         → Gemma 3 (Google)
#   "deepseek/deepseek-r1:free"          → DeepSeek R1 (raisonnement)
model: str = "meta-llama/llama-4-scout:free"

# URL de l'API OpenRouter (compatible format OpenAI)
openrouter_base_url: str = "https://openrouter.ai/api/v1"

# -- Mode LLM local (Ollama) — alternative offline totale --
local_llm_url: str = "http://localhost:11434/api/generate"
local_llm_model: str = "mistral"

# Personnalité de JARVIS
personality: str = """Tu es JARVIS, un assistant IA sophistiqué et élégant.
```

Tu es direct, efficace, légèrement sarcastique mais toujours serviable.
Tu réponds en français par défaut. Tes réponses sont concises (max 2-3 phrases).
Tu peux exécuter des commandes système, lancer des applications et aider l’utilisateur.”””
max_tokens: int = 300

@dataclass
class SpeechConfig:
stt_engine: str = “whisper”
whisper_model: str = “base”  # tiny, base, small, medium
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
