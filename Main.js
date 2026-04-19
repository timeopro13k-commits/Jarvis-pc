# Main.py

# JARVIS — Point d’entrée principal, aucune clé API requise

import asyncio
import json
import logging
import time
import sys
import os
from pathlib import Path

logging.basicConfig(
level=logging.INFO,
format=’%(asctime)s [%(name)s] %(levelname)s: %(message)s’,
handlers=[
logging.StreamHandler(sys.stdout),
logging.FileHandler(“jarvis.log”, encoding=‘utf-8’),
]
)
logger = logging.getLogger(“jarvis”)

# Les fichiers sont tous à la racine du projet

sys.path.insert(0, str(Path(**file**).parent))

from Config import CONFIG
from Clap_detector import ClapDetector
from Audio_engine import AudioEngine
from Commander import Commander
from Ai_engine import AIEngine

try:
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
except ImportError:
logger.error(“Installez FastAPI : pip install fastapi uvicorn”)
sys.exit(1)

# ── Init ──────────────────────────────────────────────────────────────────────

app = FastAPI(title=“JARVIS”, version=“1.0.0”)

clap_detector = ClapDetector(CONFIG.audio)
commander     = Commander(CONFIG)
ai_engine     = AIEngine(CONFIG)
speech_engine = None
audio_engine  = None

connected_clients: list = []

# ── WebSocket helpers ─────────────────────────────────────────────────────────

async def broadcast(message: dict):
data = json.dumps(message)
dead = []
for client in connected_clients:
try:
await client.send_text(data)
except Exception:
dead.append(client)
for c in dead:
connected_clients.remove(c)

async def send_status(status: str, data: dict = None):
await broadcast({“type”: “status”, “status”: status, “data”: data or {}, “timestamp”: time.time()})

# ── Logique principale ────────────────────────────────────────────────────────

def on_double_clap():
logger.info(“Double clap détecté — activation JARVIS”)
asyncio.run_coroutine_threadsafe(handle_wake(), asyncio.get_event_loop())

async def handle_wake():
await send_status(“waking”, {})
await speak(“Je vous écoute.”)
if audio_engine:
audio_engine.activate_voice_listening()
await send_status(“listening”, {})

def on_audio_level(level: float):
asyncio.run_coroutine_threadsafe(
broadcast({“type”: “audio_level”, “level”: level}),
asyncio.get_event_loop()
)

async def on_command(text: str):
logger.info(f”Commande : ‘{text}’”)
await send_status(“processing”, {“command”: text})

```
intent = await ai_engine.process(text)
result_msg = intent.response

if intent.action == "launch_app" and intent.target:
    result = await commander.launch_app(intent.target)
    if not result.success:
        result_msg = f"Impossible de lancer {intent.target} : {result.error}"
    else:
        await send_status("action", {"target": intent.target})

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
    await speak("À bientôt.")
    await send_status("sleeping", {})
    return

await speak(result_msg)
await send_status("idle", {"response": result_msg})
```

async def speak(text: str):
logger.info(f”Réponse : ‘{text}’”)
await broadcast({“type”: “speak”, “text”: text})
if speech_engine:
loop = asyncio.get_event_loop()
await loop.run_in_executor(None, speech_engine.speak, text)

# ── Audio ─────────────────────────────────────────────────────────────────────

def init_audio():
global audio_engine
clap_detector.on_double_clap(on_double_clap)
audio_engine = AudioEngine(CONFIG, clap_detector, speech_engine)
audio_engine.on_audio_level(on_audio_level)

```
def command_handler(text: str):
    asyncio.run_coroutine_threadsafe(on_command(text), asyncio.get_event_loop())

audio_engine.on_command(command_handler)
audio_engine.start()
logger.info("Moteur audio démarré")
```

# ── WebSocket ─────────────────────────────────────────────────────────────────

@app.websocket(”/ws”)
async def ws_endpoint(websocket: WebSocket):
await websocket.accept()
connected_clients.append(websocket)
logger.info(f”Client connecté ({len(connected_clients)} total)”)

```
await websocket.send_text(json.dumps({
    "type": "init",
    "status": "ready",
    "config": {"name": CONFIG.name, "mode": CONFIG.ai.mode}
}))

try:
    while True:
        data = await websocket.receive_text()
        msg = json.loads(data)
        await handle_msg(msg)
except WebSocketDisconnect:
    connected_clients.remove(websocket)
except Exception as e:
    logger.error(f"WebSocket erreur : {e}")
    if websocket in connected_clients:
        connected_clients.remove(websocket)
```

async def handle_msg(msg: dict):
t = msg.get(“type”)
if t == “text_command”:
text = msg.get(“text”, “”).strip()
if text:
await on_command(text)
elif t == “simulate_clap”:
await handle_wake()
elif t == “ping”:
await broadcast({“type”: “pong”, “timestamp”: time.time()})

# ── Lifecycle ─────────────────────────────────────────────────────────────────

@app.on_event(“startup”)
async def startup():
logger.info(”=” * 40)
logger.info(”  JARVIS — Démarrage (mode offline)”)
logger.info(”=” * 40)
loop = asyncio.get_event_loop()
await loop.run_in_executor(None, init_audio)
logger.info(f”WebSocket prêt → ws://localhost:{CONFIG.server.port}/ws”)

@app.on_event(“shutdown”)
async def shutdown():
if audio_engine:
audio_engine.stop()
logger.info(“JARVIS arrêté.”)

@app.get(”/health”)
async def health():
return {“status”: “ok”, “mode”: CONFIG.ai.mode}

if **name** == “**main**”:
uvicorn.run(app, host=CONFIG.server.host, port=CONFIG.server.port, log_level=“warning”)
