# Ai engine.py

“””
Interface LLM modulaire.
Supporte : OpenRouter (gratuit), Ollama (local), mode offline.
“””

import json
import logging
import re
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(“jarvis.ai”)

@dataclass
class ParsedIntent:
action: str          # “launch_app”, “query”, “open_file”, “system_info”, “speak”, “unknown”
target: str = “”
response: str = “”
raw: str = “”

OFFLINE_PATTERNS = [
(r”(?:ouvre|lance|démarre|ouvrir|lancer|start)\s+(.+)”, “launch_app”),
(r”(?:ferme|quitte)\s+(.+)”, “close_app”),
(r”(?:heure|quelle heure)”, “get_time”),
(r”(?:info|système|cpu|mémoire|ram)”, “system_info”),
(r”(?:bonjour|salut|hello)”, “greet”),
(r”(?:merci|thanks)”, “thanks”),
(r”(?:au revoir|bye|quitte|arrête)”, “quit”),
]

class AIEngine:
def **init**(self, config):
self.cfg = config.ai
self._conversation_history = []

```
async def process(self, user_input: str) -> ParsedIntent:
    logger.info(f"Traitement: '{user_input}'")

    # Parsing rapide local (pas d'API pour les commandes simples)
    quick = self._quick_parse(user_input)
    if quick:
        return quick

    # Appel API selon le mode
    if self.cfg.mode == "openrouter" and self.cfg.openrouter_api_key not in ("", "COLLEZ_VOTRE_CLÉ_ICI"):
        return await self._process_openrouter(user_input)
    elif self.cfg.mode == "local_llm":
        return await self._process_local(user_input)
    else:
        return self._process_offline(user_input)

def _quick_parse(self, text: str) -> Optional[ParsedIntent]:
    text_lower = text.lower()

    # Lancement d'app
    m = re.search(r"(?:ouvre|lance|démarre|ouvrir|lancer|start)\s+(.+)", text_lower)
    if m:
        app = re.sub(r'\b(s\'il te plaît|please|maintenant|vite)\b', '', m.group(1)).strip()
        return ParsedIntent(action="launch_app", target=app, response=f"Je lance {app}...", raw=text)

    # Heure
    if any(w in text_lower for w in ["heure", "quelle heure", "what time"]):
        from datetime import datetime
        return ParsedIntent(action="speak", response=f"Il est {datetime.now().strftime('%H:%M')}.", raw=text)

    return None

async def _process_openrouter(self, user_input: str) -> ParsedIntent:
    """Appel via OpenRouter — gratuit, compatible format OpenAI."""
    try:
        import httpx

        system_prompt = f"""{self.cfg.personality}
```

Réponds TOUJOURS en JSON avec ce format exact :
{{
“action”: “launch_app|open_file|system_info|speak|quit”,
“target”: “nom_app_ou_fichier_si_applicable”,
“response”: “ta réponse vocale courte en français”
}}”””

```
        messages = [{"role": "system", "content": system_prompt}]
        for msg in self._conversation_history[-6:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_input})

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{self.cfg.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.cfg.openrouter_api_key}",
                    "Content-Type": "application/json",
                    # Identifiant du projet (recommandé par OpenRouter)
                    "HTTP-Referer": "https://github.com/vous/jarvis-pc",
                    "X-Title": "JARVIS Desktop Assistant",
                },
                json={
                    "model": self.cfg.model,
                    "messages": messages,
                    "max_tokens": self.cfg.max_tokens,
                    "temperature": 0.7,
                }
            )

            data = resp.json()

            # Gestion d'erreur API
            if "error" in data:
                logger.error(f"OpenRouter erreur: {data['error']}")
                return self._process_offline(user_input)

            raw = data["choices"][0]["message"]["content"]

            # Historique
            self._conversation_history.append({"role": "user", "content": user_input})
            self._conversation_history.append({"role": "assistant", "content": raw})

            # Parse JSON
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
        logger.error(f"Erreur OpenRouter: {e}")
        return self._process_offline(user_input)

async def _process_local(self, user_input: str) -> ParsedIntent:
    """Traitement via Ollama (LLM local, 100% offline)."""
    try:
        import httpx
        prompt = f"""[INST] {self.cfg.personality}
```

Commande: {user_input}
Réponds en JSON: {{“action”: “speak|launch_app|system_info”, “target”: “”, “response”: “ta réponse”}} [/INST]”””

```
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                self.cfg.local_llm_url,
                json={"model": self.cfg.local_llm_model, "prompt": prompt, "stream": False}
            )
            raw = resp.json().get("response", "")
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
        logger.error(f"Erreur Ollama: {e}")
        return self._process_offline(user_input)

def _process_offline(self, user_input: str) -> ParsedIntent:
    """Fallback offline par patterns — aucune connexion requise."""
    text_lower = user_input.lower()

    for pattern, action in OFFLINE_PATTERNS:
        m = re.search(pattern, text_lower)
        if m:
            target = m.group(1).strip() if m.lastindex else ""
            responses = {
                "greet": "Bonjour. Que puis-je faire pour vous ?",
                "thanks": "Avec plaisir.",
                "quit": "À bientôt.",
                "get_time": f"Il est {__import__('datetime').datetime.now().strftime('%H:%M')}.",
            }
            return ParsedIntent(
                action=action,
                target=target,
                response=responses.get(action, f"Action: {action}"),
                raw=user_input
            )

    return ParsedIntent(
        action="speak",
        response="Je n'ai pas compris. Pourriez-vous reformuler ?",
        raw=user_input
    )
```
