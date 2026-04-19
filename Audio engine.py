# backend/core/audio_engine.py

“””
Moteur audio principal — écoute en continu en arrière-plan.
Optimisé pour faible consommation CPU.
Gère : détection de claps + VAD (Voice Activity Detection) + STT
“””

import asyncio
import logging
import threading
import numpy as np
from typing import Callable, Optional
import time

logger = logging.getLogger(“jarvis.audio”)

class AudioEngine:
“””
Moteur audio asynchrone. Tourne dans un thread dédié.
Communique avec le reste du système via callbacks.
“””

```
def __init__(self, config, clap_detector, speech_engine):
    self.cfg = config
    self.clap_detector = clap_detector
    self.speech = speech_engine
    
    # États
    self._running = False
    self._listening_for_voice = False
    self._thread: Optional[threading.Thread] = None
    
    # Callbacks
    self._on_wake: Optional[Callable] = None
    self._on_command: Optional[Callable] = None
    self._on_audio_level: Optional[Callable] = None  # Pour visualisation
    
    # Niveau audio pour visualisation (partagé thread-safe)
    self._audio_level: float = 0.0
    
def on_wake(self, callback: Callable):
    self._on_wake = callback
    return self

def on_command(self, callback: Callable):
    self._on_command = callback
    return self

def on_audio_level(self, callback: Callable):
    """Callback avec niveau audio 0-1 pour la visualisation UI."""
    self._on_audio_level = callback
    return self

@property
def audio_level(self) -> float:
    return self._audio_level

def start(self):
    """Démarre le moteur audio dans un thread dédié."""
    if self._running:
        return
    
    self._running = True
    self._thread = threading.Thread(target=self._audio_loop, daemon=True)
    self._thread.start()
    logger.info("Moteur audio démarré")

def stop(self):
    """Arrête le moteur audio proprement."""
    self._running = False
    if self._thread:
        self._thread.join(timeout=2.0)
    logger.info("Moteur audio arrêté")

def activate_voice_listening(self):
    """Active l'écoute vocale (après détection de clap)."""
    self._listening_for_voice = True
    logger.info("Écoute vocale activée")

def deactivate_voice_listening(self):
    self._listening_for_voice = False

def _audio_loop(self):
    """
    Boucle principale audio.
    Utilise sounddevice pour capturer le micro en continu.
    """
    try:
        import sounddevice as sd
    except ImportError:
        logger.error("sounddevice non installé: pip install sounddevice")
        self._run_simulation_mode()
        return
    
    cfg = self.cfg.audio
    logger.info(f"Capture audio: {cfg.sample_rate}Hz, chunk={cfg.chunk_size}")
    
    # Buffer pour accumulation de voix
    voice_buffer = []
    voice_timeout = 0.0
    
    def audio_callback(indata, frames, time_info, status):
        """Callback appelé par sounddevice pour chaque chunk."""
        if status:
            logger.debug(f"Audio status: {status}")
        
        chunk = indata[:, 0]  # Mono
        
        # Niveau audio pour visualisation
        level = float(np.sqrt(np.mean(chunk ** 2)))
        self._audio_level = min(1.0, level * 8)
        if self._on_audio_level:
            self._on_audio_level(self._audio_level)
        
        # Détection de clap (seulement si pas en mode écoute vocale)
        if not self._listening_for_voice:
            self.clap_detector.process_chunk(chunk)
        else:
            # Mode écoute vocale : accumule le buffer
            voice_buffer.append(chunk.copy())
    
    try:
        with sd.InputStream(
            samplerate=cfg.sample_rate,
            channels=cfg.channels,
            blocksize=cfg.chunk_size,
            dtype='float32',
            callback=audio_callback
        ):
            logger.info("✅ Microphone ouvert, en écoute...")
            while self._running:
                time.sleep(0.1)
                
                # Traitement de la voix si buffer accumulé
                if self._listening_for_voice and voice_buffer:
                    current_time = time.time()
                    if current_time - voice_timeout > 0.3:
                        voice_timeout = current_time
                    
                    # Arrête après 4 secondes de silence ou 10 secondes max
                    if len(voice_buffer) > (cfg.sample_rate / cfg.chunk_size) * 8:
                        self._process_voice_buffer(voice_buffer[:])
                        voice_buffer.clear()
                        self._listening_for_voice = False
    
    except Exception as e:
        logger.error(f"Erreur audio: {e}")
        logger.info("Passage en mode simulation")
        self._run_simulation_mode()

def _process_voice_buffer(self, buffer: list):
    """Traite le buffer vocal accumulé avec STT."""
    if not buffer:
        return
    
    audio_data = np.concatenate(buffer)
    logger.info(f"Traitement vocal: {len(audio_data)} samples")
    
    try:
        text = self.speech.transcribe(audio_data, self.cfg.audio.sample_rate)
        if text and len(text.strip()) > 2:
            logger.info(f"Commande reconnue: '{text}'")
            if self._on_command:
                self._on_command(text.strip())
    except Exception as e:
        logger.error(f"Erreur STT: {e}")

def _run_simulation_mode(self):
    """
    Mode simulation si pas de micro disponible.
    Utile pour le développement.
    """
    logger.warning("🔧 Mode simulation audio (pas de micro)")
    import math
    t = 0
    while self._running:
        # Simule un niveau audio oscillant
        self._audio_level = (math.sin(t * 2) + 1) / 2 * 0.3
        if self._on_audio_level:
            self._on_audio_level(self._audio_level)
        t += 0.1
        time.sleep(0.05)
```
