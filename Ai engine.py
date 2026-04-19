# Ai engine.py

“””
Interface IA de JARVIS — 100% offline, aucune clé requise.
Mode “offline”   : patterns locaux, instantané.
Mode “local_llm” : Ollama (optionnel, plus intelligent).
“””

import re
import json
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(“jarvis.ai”)

@dataclass
class ParsedIntent:
action: str   # “launch_app”, “system_info”, “speak”, “get_time”, “quit”
target: str = “”
response: str = “”
raw: str = “”

# ── Patterns de reconnaissance de commandes ───────────────────────────────────

PATTERNS = [
# Lancement d’applications
(r”(?:ouvre|lance|démarre|ouvrir|lancer|start|exécute)\s+(.+)”, “launch_app”),
# Informations système
(r”(?:cpu|ram|mémoire|disque|système|system|info)”, “system_info”),
# Heure et date
(r”(?:heure|quelle heure|time|date|jour)”, “get_time”),
# Météo (réponse locale simple)
(r”(?:météo|temps qu’il fait|weather)”, “weather”),
# Calcul simple
(r”(?:calcule|combien|combien font|calcul)\s+(.+)”, “calculate”),
# Salutations
(r”(?:bonjour|salut|hello|bonsoir|coucou)”, “greet”),
(r”(?:merci|thanks|thank you)”, “thanks”),
(r”(?:comment tu vas|ça va|how are you)”, “how_are_you”),
# Quitter
(r”(?:au revoir|bye|quitte|arrête|stop|ferme toi)”, “quit”),
# Blague
(r”(?:blague|joke|fais moi rire)”, “joke”),
# Aide
(r”(?:aide|help|que sais.tu faire|commandes)”, “help”),
]

JOKES = [
“Pourquoi les robots ne mangent-ils pas ? Parce qu’ils ont déjà un byte.”,
“Comment appelle-t-on un chat tombé dans un pot de peinture ? Un chat-peint.”,
“Qu’est-ce qu’un crocodile qui surveille la cour d’école ? Un sac à dents.”,
“Pourquoi l’épouvantail a-t-il eu un prix ? Parce qu’il était exceptionnel dans son domaine.”,
]

HELP_TEXT = (
“Je peux : lancer des applications, donner l’heure, “
“les infos système, faire des calculs simples, “
“raconter des blagues. Essayez ‘lance Chrome’ ou ‘quelle heure est-il’.”
)

class AIEngine:
def **init**(self, config):
self.cfg = config.ai
self._joke_index = 0

```
async def process(self, user_input: str) -> ParsedIntent:
    logger.info(f"Traitement: '{user_input}'")

    if self.cfg.mode == "local_llm":
        result = await self._process_ollama(user_input)
        if result:
            return result
        # Fallback sur offline si Ollama échoue
        logger.warning("Ollama indisponible, fallback offline")

    return self._process_offline(user_input)

def _process_offline(self, user_input: str) -> ParsedIntent:
    """Reconnaissance par patterns — instantané, aucune connexion."""
    text = user_input.lower().strip()

    for pattern, action in PATTERNS:
        m = re.search(pattern, text)
        if m:
            target = m.group(1).strip() if m.lastindex else ""
            # Nettoyer les mots parasites dans le nom d'app
            if action == "launch_app":
                target = re.sub(
                    r'\b(s\'il te plaît|please|maintenant|vite|pour moi)\b',
                    '', target
                ).strip()

            response = self._build_response(action, target, user_input)
            return ParsedIntent(action=action, target=target, response=response, raw=user_input)

    # Aucun pattern trouvé
    return ParsedIntent(
        action="speak",
        response="Je n'ai pas compris. Dites 'aide' pour voir ce que je sais faire.",
        raw=user_input
    )

def _build_response(self, action: str, target: str, raw: str) -> str:
    """Construit la réponse textuelle selon l'action."""
    from datetime import datetime

    if action == "launch_app":
        return f"Je lance {target}."

    elif action == "system_info":
        return "Je récupère les informations système."

    elif action == "get_time":
        now = datetime.now()
        return f"Il est {now.strftime('%H:%M')}, nous sommes le {now.strftime('%A %d %B %Y')}."

    elif action == "weather":
        return "Je n'ai pas accès à internet, mais j'espère qu'il fait beau chez vous."

    elif action == "calculate":
        return self._safe_calculate(target)

    elif action == "greet":
        from datetime import datetime
        h = datetime.now().hour
        salut = "Bonsoir" if h >= 18 else "Bonjour"
        return f"{salut}. Tous les systèmes sont opérationnels. Que puis-je faire pour vous ?"

    elif action == "thanks":
        return "Avec plaisir. C'est pour cela que j'existe."

    elif action == "how_are_you":
        return "Tous mes systèmes fonctionnent parfaitement. Merci de vous en préoccuper."

    elif action == "quit":
        return "À bientôt. Mise en veille."

    elif action == "joke":
        joke = JOKES[self._joke_index % len(JOKES)]
        self._joke_index += 1
        return joke

    elif action == "help":
        return HELP_TEXT

    return "Commande reçue."

def _safe_calculate(self, expression: str) -> str:
    """Calcul simple et sécurisé (pas d'eval dangereux)."""
    try:
        # Remplace les mots par des opérateurs
        expr = expression
        expr = re.sub(r'\bplus\b', '+', expr)
        expr = re.sub(r'\bmoins\b', '-', expr)
        expr = re.sub(r'\bfois\b|\bmultiplié par\b', '*', expr)
        expr = re.sub(r'\bdivisé par\b', '/', expr)

        # Garde uniquement chiffres et opérateurs basiques
        clean = re.sub(r'[^0-9+\-*/().\s]', '', expr).strip()
        if not clean:
            return "Je n'ai pas pu interpréter ce calcul."

        result = eval(clean, {"__builtins__": {}}, {})
        return f"Le résultat est {round(result, 4)}."
    except Exception:
        return "Je n'ai pas pu effectuer ce calcul."

async def _process_ollama(self, user_input: str) -> Optional[ParsedIntent]:
    """Ollama local — optionnel, plus intelligent que les patterns."""
    try:
        import httpx

        prompt = f"""{self.cfg.personality}
```

L’utilisateur dit : “{user_input}”

Réponds en JSON uniquement :
{{“action”: “launch_app|system_info|speak|quit”, “target”: “”, “response”: “ta réponse en français”}}”””

```
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                self.cfg.local_llm_url,
                json={
                    "model": self.cfg.local_llm_model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            raw = resp.json().get("response", "")
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if m:
                parsed = json.loads(m.group())
                return ParsedIntent(
                    action=parsed.get("action", "speak"),
                    target=parsed.get("target", ""),
                    response=parsed.get("response", raw),
                    raw=user_input
                )
    except Exception as e:
        logger.debug(f"Ollama non disponible: {e}")

    return None
```
