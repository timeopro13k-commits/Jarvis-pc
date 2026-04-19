# backend/main.py

“””
Point d’entrée principal de JARVIS.
Serveur FastAPI + WebSocket pour communication avec le frontend.
“””

import asyncio
import json
import logging
import time
import sys
import os
from pathlib import Path

# Setup du logging

logging.basicConfig(
level=logging.INFO,
format=’%(asctime)s [%(name)s] %(levelname)s: %(message)s’,
handlers=[
logging.StreamHandler(sys.stdout),
logging.FileHandler(“jarvis.log”, encoding=‘utf-8’),
]
)
logger = logging.getLogger(“jarvis”)

# Imports du projet

sys.path.insert(0, str(Path(**file**).parent))
from config import CONFIG
from core.clap_detector import ClapDetector
from core.audio_engine import AudioEngine
from core.commander import Commander
from core.ai_engine import AIEngine

try:
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn
except ImportError:
logger.error(“FastAPI/uvicorn non installé: pip install fastapi uvicorn”)
sys.exit(1)

# ─── Initialisation des modules ───────────────────────────────────────────────

app = FastAPI(title=“JARVIS Backend”, version=“1.0.0”)

# Instances globales

clap_detector = ClapDetector(CONFIG.audio)
commander = Commander(CONFIG)
ai_engine = AIEngine(CONFIG)

# STT/TTS (import lazy pour éviter les délais au démarrage)

speech_engine = None

# WebSocket clients connectés

connected_clients: list[WebSocket] = []

# ─── Utilitaires WebSocket ─────────────────────────────────────────────────────

async def broadcast(message: dict):
“”“Envoie un message à tous les clients WebSocket connectés.”””
if not connected_clients:
return

```
data = json.dumps(message)
dead_clients = []

for client in connected_clients:
    try:
        await client.send_text(data)
    except Exception:
        dead_clients.append(client)

for c in dead_clients:
    connected_clients.remove(c)
```

async def send_status(status: str, data: dict = None):
“”“Envoie un message de statut au frontend.”””
await broadcast({
“type”: “status”,
“status”: status,
“data”: data or {},
“timestamp”: time.time()
})

# ─── Callbacks système ────────────────────────────────────────────────────────

def on_double_clap():
“”“Déclenché quand un double clap est détecté.”””
logger.info(“🎯 Double clap → Activation JARVIS”)
asyncio.run_coroutine_threadsafe(
handle_wake_event(),
asyncio.get_event_loop()
)

async def handle_wake_event():
“”“Gestion de l’événement de réveil.”””
await send_status(“waking”, {“message”: “Activation par clap détectée”})

```
# Feedback sonore
await speak("Je vous écoute.")

# Active l'écoute vocale
if audio_engine:
    audio_engine.activate_voice_listening()

await send_status("listening", {"message": "En écoute..."})
```

def on_audio_level(level: float):
“”“Callback niveau audio pour visualisation temps réel.”””
asyncio.run_coroutine_threadsafe(
broadcast({“type”: “audio_level”, “level”: level}),
asyncio.get_event_loop()
)

async def on_voice_command(text: str):
“”“Traite une commande vocale reconnue.”””
logger.info(f”Commande vocale: ‘{text}’”)

```
await send_status("processing", {"command": text})

# Parse l'intention via IA
intent = await ai_engine.process(text)
logger.info(f"Intent: action={intent.action}, target={intent.target}")

# Exécution de l'action
result_msg = intent.response

if intent.action == "launch_app" and intent.target:
    result = await commander.launch_app(intent.target)
    if not result.success:
        result_msg = f"Impossible de lancer {intent.target}: {result.error}"
    else:
        await send_status("action", {
            "action": "launched",
            "target": intent.target
        })

elif intent.action == "system_info":
    info = await commander.get_system_info()
    if info:
        result_msg = (
            f"CPU à {info['cpu_percent']}%, "
            f"mémoire à {info['memory']['percent']}%."
        )

elif intent.action == "open_file" and intent.target:
    result = await commander.open_file(intent.target)
    if not result.success:
        result_msg = result.error

elif intent.action == "quit":
    await speak("Au revoir.")
    await send_status("sleeping", {})
    return

# Réponse vocale
await speak(result_msg)
await send_status("idle", {"last_command": text, "response": result_msg})
```

async def speak(text: str):
“”“Synthèse vocale + envoi au frontend pour affichage.”””
logger.info(f”TTS: ‘{text}’”)
await broadcast({“type”: “speak”, “text”: text})

```
# TTS en arrière-plan (non bloquant)
if speech_engine:
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, speech_engine.speak, text)
```

# ─── Initialisation des modules audio ─────────────────────────────────────────

audio_engine = None

def init_audio():
“”“Initialise le moteur audio (dans le thread principal).”””
global audio_engine

```
# Setup clap detector callback
clap_detector.on_double_clap(on_double_clap)

# Créer audio engine (speech_engine peut être None en mode dégradé)
audio_engine = AudioEngine(CONFIG, clap_detector, speech_engine)
audio_engine.on_audio_level(on_audio_level)

# Le callback on_command doit être async-compatible
def command_handler(text: str):
    asyncio.run_coroutine_threadsafe(
        on_voice_command(text),
        asyncio.get_event_loop()
    )

audio_engine.on_command(command_handler)
audio_engine.start()
logger.info("✅ Moteur audio initialisé")
```

# ─── Routes WebSocket ─────────────────────────────────────────────────────────

@app.websocket(”/ws”)
async def websocket_endpoint(websocket: WebSocket):
“”“Endpoint WebSocket principal.”””
await websocket.accept()
connected_clients.append(websocket)
logger.info(f”Client connecté. Total: {len(connected_clients)}”)

```
# Envoi de l'état initial
await websocket.send_text(json.dumps({
    "type": "init",
    "status": "ready",
    "config": {
        "name": CONFIG.name,
        "mode": CONFIG.ai.mode,
    }
}))

try:
    while True:
        data = await websocket.receive_text()
        msg = json.loads(data)
        await handle_frontend_message(msg)

except WebSocketDisconnect:
    connected_clients.remove(websocket)
    logger.info(f"Client déconnecté. Total: {len(connected_clients)}")
except Exception as e:
    logger.error(f"Erreur WebSocket: {e}")
    if websocket in connected_clients:
        connected_clients.remove(websocket)
```

async def handle_frontend_message(msg: dict):
“”“Traite les messages entrants du frontend.”””
msg_type = msg.get(“type”)

```
if msg_type == "text_command":
    # Commande textuelle (depuis l'input clavier du frontend)
    text = msg.get("text", "").strip()
    if text:
        await on_voice_command(text)

elif msg_type == "simulate_clap":
    # Simule un double clap (pour tests)
    await handle_wake_event()

elif msg_type == "ping":
    await broadcast({"type": "pong", "timestamp": time.time()})
```

# ─── Lifecycle ────────────────────────────────────────────────────────────────

@app.on_event(“startup”)
async def startup():
logger.info(”=” * 50)
logger.info(”  JARVIS v1.0 — Démarrage”)
logger.info(”=” * 50)

```
# Init audio dans un executor pour ne pas bloquer
loop = asyncio.get_event_loop()
await loop.run_in_executor(None, init_audio)

logger.info(f"✅ WebSocket prêt sur ws://localhost:{CONFIG.server.port}/ws")
```

@app.on_event(“shutdown”)
async def shutdown():
if audio_engine:
audio_engine.stop()
logger.info(“JARVIS arrêté.”)

@app.get(”/health”)
async def health():
return {“status”: “ok”, “name”: CONFIG.name}

# ─── Point d’entrée ───────────────────────────────────────────────────────────

if **name** == “**main**”:
uvicorn.run(
app,
host=CONFIG.server.host,
port=CONFIG.server.port,
log_level=“warning”,  # Réduit le bruit uvicorn
)
