# backend/core/commander.py

“””
Exécuteur de commandes système sécurisé.
Sandbox, liste blanche, journalisation, confirmation obligatoire pour actions critiques.
“””

import asyncio
import subprocess
import platform
import logging
import shutil
from typing import Optional
from pathlib import Path

logger = logging.getLogger(“jarvis.commander”)

# Mapping des noms d’apps vers les commandes par OS

APP_COMMANDS = {
“darwin”: {  # macOS
“chrome”: “open -a ‘Google Chrome’”,
“firefox”: “open -a Firefox”,
“safari”: “open -a Safari”,
“code”: “open -a ‘Visual Studio Code’”,
“vscode”: “open -a ‘Visual Studio Code’”,
“terminal”: “open -a Terminal”,
“finder”: “open -a Finder”,
“spotify”: “open -a Spotify”,
“calculator”: “open -a Calculator”,
“notes”: “open -a Notes”,
},
“linux”: {
“chrome”: “google-chrome”,
“firefox”: “firefox”,
“code”: “code”,
“vscode”: “code”,
“terminal”: “x-terminal-emulator”,
“files”: “nautilus”,
“spotify”: “spotify”,
“calculator”: “gnome-calculator”,
},
“windows”: {
“chrome”: r”start chrome”,
“firefox”: r”start firefox”,
“code”: r”start code”,
“vscode”: r”start code”,
“terminal”: r”start cmd”,
“files”: r”explorer”,
“notepad”: r”start notepad”,
“calculator”: r”start calc”,
}
}

class CommandResult:
def **init**(self, success: bool, output: str = “”, error: str = “”):
self.success = success
self.output = output
self.error = error

```
def __str__(self):
    return self.output if self.success else f"Erreur: {self.error}"
```

class Commander:
“”“Exécute des commandes système de manière sécurisée.”””

```
def __init__(self, config):
    self.cfg = config.security
    self.os_name = platform.system().lower()
    self._pending_confirmations = {}
    
async def launch_app(self, app_name: str) -> CommandResult:
    """
    Lance une application par son nom.
    Vérifie la liste blanche avant d'exécuter.
    """
    app_lower = app_name.lower().strip()
    
    # Vérification liste blanche
    allowed = [a.lower() for a in self.cfg.allowed_apps]
    if app_lower not in allowed:
        logger.warning(f"Application non autorisée: {app_name}")
        return CommandResult(
            success=False,
            error=f"'{app_name}' n'est pas dans la liste des applications autorisées."
        )
    
    # Résolution de la commande par OS
    os_apps = APP_COMMANDS.get(self.os_name, {})
    cmd = os_apps.get(app_lower)
    
    if not cmd:
        # Tentative générique : cherche l'exécutable dans PATH
        if shutil.which(app_lower):
            cmd = app_lower
        else:
            return CommandResult(
                success=False,
                error=f"Application '{app_name}' introuvable sur {self.os_name}"
            )
    
    logger.info(f"Lancement: {app_name} -> {cmd}")
    return await self._execute_safe(cmd, shell=True)

async def get_system_info(self) -> dict:
    """Récupère des informations système basiques (sûres)."""
    import psutil
    
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": {
                "total": psutil.virtual_memory().total,
                "used": psutil.virtual_memory().used,
                "percent": psutil.virtual_memory().percent,
            },
            "disk": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "percent": psutil.disk_usage('/').percent,
            },
            "platform": platform.system(),
            "hostname": platform.node(),
        }
    except Exception as e:
        logger.error(f"Erreur infos système: {e}")
        return {}

async def open_file(self, filepath: str) -> CommandResult:
    """
    Ouvre un fichier avec l'application par défaut.
    Vérifie que le fichier existe et est accessible.
    """
    path = Path(filepath)
    
    if not path.exists():
        return CommandResult(success=False, error=f"Fichier introuvable: {filepath}")
    
    # Seulement les fichiers dans le home directory (sécurité)
    home = Path.home()
    try:
        path.relative_to(home)
    except ValueError:
        return CommandResult(
            success=False,
            error="Accès refusé: seuls les fichiers dans votre dossier personnel sont accessibles."
        )
    
    if self.os_name == "darwin":
        cmd = f"open '{filepath}'"
    elif self.os_name == "linux":
        cmd = f"xdg-open '{filepath}'"
    else:
        cmd = f"start '' '{filepath}'"
    
    return await self._execute_safe(cmd, shell=True)

def requires_confirmation(self, command: str) -> bool:
    """Vérifie si une commande nécessite une confirmation."""
    cmd_lower = command.lower()
    return any(danger in cmd_lower for danger in self.cfg.require_confirmation)

async def _execute_safe(self, command: str, shell: bool = False, timeout: int = 10) -> CommandResult:
    """
    Exécution sécurisée avec timeout.
    Journalise toutes les exécutions.
    """
    logger.info(f"EXEC: {command}")
    
    try:
        if shell:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        else:
            args = command.split()
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), 
            timeout=timeout
        )
        
        if proc.returncode == 0:
            return CommandResult(success=True, output=stdout.decode('utf-8', errors='ignore'))
        else:
            return CommandResult(
                success=False,
                error=stderr.decode('utf-8', errors='ignore')
            )
    
    except asyncio.TimeoutError:
        return CommandResult(success=False, error="Délai d'exécution dépassé")
    except Exception as e:
        logger.error(f"Erreur exécution: {e}")
        return CommandResult(success=False, error=str(e))
```
