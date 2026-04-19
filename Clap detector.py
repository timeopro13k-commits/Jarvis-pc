# backend/core/clap_detector.py

“””
Détecteur de claps optimisé — faible CPU.
Algorithme : analyse de l’énergie RMS + détection de transitoire.
Pas de ML, pas de modèle lourd. Fonctionne en temps réel.
“””

import numpy as np
import time
import logging
from typing import Callable, Optional
from dataclasses import dataclass

logger = logging.getLogger(“jarvis.clap”)

@dataclass
class ClapEvent:
timestamp: float
intensity: float  # 0.0 - 1.0

class ClapDetector:
“””
Détecte les doubles claquements de mains dans un flux audio.

```
Principe :
1. Calcule l'énergie RMS du chunk audio
2. Détecte un spike soudain (transitoire) au-dessus du seuil
3. Vérifie si 2 spikes arrivent dans la fenêtre temporelle définie
4. Confirme le double clap
"""

def __init__(self, config):
    self.cfg = config
    self.sample_rate = config.sample_rate
    
    # Historique des claps détectés
    self._clap_history: list[ClapEvent] = []
    
    # Noise floor adaptatif (s'ajuste au bruit ambiant)
    self._noise_floor: float = 0.01
    self._noise_samples: list[float] = []
    self._noise_calibrated: bool = False
    
    # Anti-rebond : évite de détecter le même clap plusieurs fois
    self._last_clap_time: float = 0.0
    
    # Callback déclenché sur double clap confirmé
    self._on_double_clap: Optional[Callable] = None
    
    # État interne
    self._cooldown_until: float = 0.0
    
    logger.info("ClapDetector initialisé")

def on_double_clap(self, callback: Callable):
    """Enregistre le callback appelé lors d'un double clap."""
    self._on_double_clap = callback
    return self

def calibrate(self, audio_chunk: np.ndarray):
    """
    Calibration du bruit ambiant sur les premières secondes.
    Permet d'adapter le seuil à l'environnement.
    """
    rms = self._compute_rms(audio_chunk)
    self._noise_samples.append(rms)
    
    # Calibration sur ~2 secondes
    if len(self._noise_samples) >= (self.sample_rate // 1024) * 2:
        self._noise_floor = np.mean(self._noise_samples) * 1.5
        self._noise_calibrated = True
        logger.info(f"Calibration terminée. Noise floor: {self._noise_floor:.4f}")

def process_chunk(self, audio_chunk: np.ndarray) -> bool:
    """
    Analyse un chunk audio et retourne True si double clap détecté.
    
    Args:
        audio_chunk: Tableau numpy float32, valeurs -1.0 à 1.0
    
    Returns:
        True si double clap confirmé
    """
    # Phase de calibration
    if not self._noise_calibrated:
        self.calibrate(audio_chunk)
        return False
    
    # En cooldown après un double clap
    now = time.time()
    if now < self._cooldown_until:
        return False
    
    # Calcul de l'énergie du chunk
    rms = self._compute_rms(audio_chunk)
    
    # Détection de transitoire : spike soudain au-dessus du seuil
    dynamic_threshold = self._noise_floor + (self.cfg.clap_threshold * 0.5)
    
    if rms > dynamic_threshold and self._is_transient(audio_chunk):
        # Anti-rebond : ignorer si trop proche du dernier clap
        if now - self._last_clap_time < self.cfg.clap_min_interval:
            return False
        
        intensity = min(1.0, rms / (dynamic_threshold * 3))
        clap = ClapEvent(timestamp=now, intensity=intensity)
        self._clap_history.append(clap)
        self._last_clap_time = now
        
        logger.debug(f"Clap détecté! RMS={rms:.3f}, Intensité={intensity:.2f}")
        
        # Nettoyer l'historique (garder seulement les claps récents)
        self._prune_history(now)
        
        # Vérifier si double clap
        if self._check_double_clap(now):
            logger.info("✅ DOUBLE CLAP CONFIRMÉ!")
            self._cooldown_until = now + self.cfg.clap_cooldown
            self._clap_history.clear()
            
            if self._on_double_clap:
                self._on_double_clap()
            return True
    
    return False

def _compute_rms(self, chunk: np.ndarray) -> float:
    """Calcule l'énergie RMS (Root Mean Square) du signal."""
    return float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))

def _is_transient(self, chunk: np.ndarray) -> bool:
    """
    Vérifie si le chunk contient un transitoire (attaque soudaine).
    Un clap a une montée très rapide, contrairement à un son continu.
    """
    chunk_f = chunk.astype(np.float32)
    
    # Divise le chunk en 4 parties et compare l'énergie
    quarter = len(chunk_f) // 4
    if quarter == 0:
        return True
    
    first_quarter_rms = np.sqrt(np.mean(chunk_f[:quarter] ** 2))
    rest_rms = np.sqrt(np.mean(chunk_f[quarter:] ** 2))
    
    # Un clap : première partie beaucoup plus forte
    if first_quarter_rms > 0.001:
        ratio = rest_rms / first_quarter_rms
        return ratio < 0.8  # Décroissance rapide = transitoire
    
    return False

def _prune_history(self, now: float):
    """Supprime les claps trop anciens de l'historique."""
    cutoff = now - self.cfg.clap_max_interval * 2
    self._clap_history = [c for c in self._clap_history if c.timestamp > cutoff]

def _check_double_clap(self, now: float) -> bool:
    """
    Vérifie si les derniers claps forment un double clap.
    Conditions :
    - Au moins 2 claps dans l'historique
    - Intervalle entre les 2 derniers claps dans la fenêtre [min, max]
    """
    if len(self._clap_history) < 2:
        return False
    
    # Prendre les 2 derniers claps
    recent = self._clap_history[-2:]
    interval = recent[1].timestamp - recent[0].timestamp
    
    return self.cfg.clap_min_interval <= interval <= self.cfg.clap_max_interval
```
