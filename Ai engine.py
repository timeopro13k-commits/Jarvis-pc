# backend/core/ai_engine.py

“””
Interface LLM modulaire.
Supporte : OpenAI, Ollama (local), mode offline basique.
Parse les intentions utilisateur et retourne des actions structurées.
“””

import json
import logging
import asyncio
import re
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(“jarvis.ai”)

@dataclass
class ParsedIntent:
“”“Résultat du parsing d’une commande utilisateur.”””
action: str          # “launch_app”, “query”, “open_file”, “system_info”, “unknown”
target: str = “”     # Application, fichier, etc.
response: str = “”   # Réponse textuelle de l’IA
raw: str = “”        # Texte brut de l’intent

# Patterns pour le mode offline (sans API)

OFFLINE_PATTERNS = [
(r”(?:ouvre|lance|démarre|ouvrir|lancer)\s+(.+)”, “launch_app”),
(r”(?:ferme|quitte)\s+(.+)”, “close_app”),
(r”(?:heure|quelle heure)”, “get_time”),
(r”(?:info|système|cpu|mémoire|ram)”, “system_info”),
(r”(?:bonjour|salut|hello)”, “greet”),
(r”(?:merci|thanks)”, “thanks”),
(r”(?:au revoir|bye|quitte|arrête)”, “quit”),
]

OFFLINE_RESPONSES = {
“greet”: “Bonjour. Que puis-je faire pour vous ?”,
“thanks”: “Avec plaisir.”,
“quit”: “À bientôt.”,
“get_time”: None,  # Géré dynamiquement
“system_info”: None,  # Géré dynamiquement
}

class AIEngine:
“”“Interface LLM avec fallback offline.”””

```
def __init__(self, config):
    self.cfg = config.ai
    self.personality = self.cfg.personality
    self._conversation_history = []
    
async def process(self, user_input: str) -> ParsedIntent:
    """
    Traite une entrée utilisateur et retourne une intention parsée.
    Essaie l'API configurée, fallback en mode offline si erreur.
    """
    logger.info(f"Traitement: '{user_input}'")
    
    # D'abord : patterns locaux rapides (pas d'API pour les commandes simples)
    quick_intent = self._quick_parse(user_input)
    if quick_intent:
        return quick_intent
    
    # Ensuite : LLM selon le mode configuré
    if self.cfg.mode == "openai" and self.cfg.openai_api_key:
        return await self._process_openai(user_input)
    elif self.cfg.mode == "local_llm":
        return await self._process_local(user_input)
    else:
        return self._process_offline(user_input)

def _quick_parse(self, text: str) -> Optional[ParsedIntent]:
    """
    Parsing rapide sans API pour les commandes évidentes.
    Evite un aller-retour réseau pour des commandes simples.
    """
    text_lower = text.lower()
    
    # Patterns de lancement d'applications
    launch_patterns = [
        r"(?:ouvre|lance|démarre|ouvrir|lancer|start)\s+(.+)",
        r"(.+?)\s+(?:s'il te plaît|please|maintenant)",
    ]
    
    for pattern in launch_patterns:
        m = re.search(pattern, text_lower)
        if m:
            app_name = m.group(1).strip()
            # Nettoyer : supprimer mots parasites
            app_name = re.sub(r'\b(s\'il te plaît|please|maintenant|vite)\b', '', app_name).strip()
            
            return ParsedIntent(
                action="launch_app",
                target=app_name,
                response=f"Je lance {app_name}...",
                raw=text
            )
    
    # Heure
    if any(w in text_lower for w in ["heure", "quelle heure", "what time"]):
        from datetime import datetime
        now = datetime.now().strftime("%H:%M")
        return ParsedIntent(
            action="speak",
            response=f"Il est {now}.",
            raw=text
        )
    
    return None

async def _process_openai(self, user_input: str) -> ParsedIntent:
    """Traitement via OpenAI API."""
    try:
        import httpx
        
        # Construction du prompt avec contexte de commandes
        system_prompt = f"""{self.personality}
```

Tu as accès aux actions suivantes. Réponds TOUJOURS en JSON avec ce format :
{{
“action”: “launch_app|open_file|system_info|speak|quit”,
“target”: “nom_de_l_app_ou_fichier”,
“response”: “ta réponse vocale courte”
}}

Actions disponibles :

- launch_app : lancer une application (target = nom de l’app)
- open_file : ouvrir un fichier (target = chemin)
- system_info : afficher les infos système
- speak : juste répondre verbalement
- quit : arrêter JARVIS”””
  
  ```
        messages = [{"role": "system", "content": system_prompt}]
        
        # Historique conversationnel (3 derniers échanges)
        for msg in self._conversation_history[-6:]:
            messages.append(msg)
        
        messages.append({"role": "user", "content": user_input})
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.cfg.openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.cfg.model,
                    "messages": messages,
                    "max_tokens": self.cfg.max_tokens,
                    "temperature": 0.7,
                }
            )
            
            data = response.json()
            raw_response = data["choices"][0]["message"]["content"]
            
            # Mise à jour historique
            self._conversation_history.append({"role": "user", "content": user_input})
            self._conversation_history.append({"role": "assistant", "content": raw_response})
            
            # Parse JSON
            try:
                # Extrait le JSON même si entouré de texte
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    return ParsedIntent(
                        action=parsed.get("action", "speak"),
                        target=parsed.get("target", ""),
                        response=parsed.get("response", raw_response),
                        raw=user_input
                    )
            except json.JSONDecodeError:
                pass
            
            return ParsedIntent(action="speak", response=raw_response, raw=user_input)
    
    except Exception as e:
        logger.error(f"Erreur OpenAI: {e}")
        return self._process_offline(user_input)
  ```
  
  async def _process_local(self, user_input: str) -> ParsedIntent:
  “”“Traitement via Ollama (LLM local).”””
  try:
  import httpx
  
  ```
        prompt = f"""[INST] {self.personality}
  ```

Commande: {user_input}

Réponds en JSON: {{“action”: “speak|launch_app|system_info”, “target”: “”, “response”: “ta réponse”}} [/INST]”””

```
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.cfg.local_llm_url,
                json={"model": self.cfg.local_llm_model, "prompt": prompt, "stream": False}
            )
            data = response.json()
            raw = data.get("response", "")
            
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return ParsedIntent(
                    action=parsed.get("action", "speak"),
                    target=parsed.get("target", ""),
                    response=parsed.get("response", raw),
                    raw=user_input
                )
            
            return ParsedIntent(action="speak", response=raw, raw=user_input)
    
    except Exception as e:
        logger.error(f"Erreur LLM local: {e}")
        return self._process_offline(user_input)

def _process_offline(self, user_input: str) -> ParsedIntent:
    """Mode offline : matching par patterns simples."""
    text_lower = user_input.lower()
    
    for pattern, action in OFFLINE_PATTERNS:
        m = re.search(pattern, text_lower)
        if m:
            target = m.group(1).strip() if m.lastindex else ""
            response = OFFLINE_RESPONSES.get(action, f"Action: {action}")
            
            if action == "get_time":
                from datetime import datetime
                response = f"Il est {datetime.now().strftime('%H:%M')}."
            
            return ParsedIntent(action=action, target=target, response=response, raw=user_input)
    
    return ParsedIntent(
        action="speak",
        response="Je n'ai pas compris. Pourriez-vous reformuler ?",
        raw=user_input
    )
```
