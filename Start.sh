#!/bin/bash

# start.sh — Démarrage JARVIS (Linux/macOS)

echo “”
echo “  ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗”
echo “  ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝”
echo “  ██║███████║██████╔╝██║   ██║██║███████╗”
echo “  ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║”
echo “  ██║██║  ██║██║  ██║ ╚████╔╝ ██║███████║”
echo “  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝”
echo “”
echo “  Assistant IA Desktop v1.0”
echo “”

# Vérifie Python

if ! command -v python3 &>/dev/null; then
echo “❌ Python 3 requis. Installation: https://python.org”
exit 1
fi

# Vérifie Node.js

if ! command -v node &>/dev/null; then
echo “❌ Node.js requis. Installation: https://nodejs.org”
exit 1
fi

# Install dépendances Python si nécessaire

if [ ! -f “.deps_installed” ]; then
echo “📦 Installation des dépendances Python…”
pip3 install -r requirements.txt –quiet
touch .deps_installed
fi

# Install dépendances Electron si nécessaire

if [ ! -d “electron/node_modules” ]; then
echo “📦 Installation des dépendances Electron…”
cd electron && npm install –silent && cd ..
fi

# Clé API OpenAI (optionnelle)

if [ -n “$OPENAI_API_KEY” ]; then
echo “✅ Clé OpenAI détectée”
else
echo “ℹ️  Pas de clé OpenAI (mode offline). Définissez OPENAI_API_KEY pour activer l’IA.”
fi

echo “”
echo “🚀 Démarrage de JARVIS…”
echo “”

# Option 1 : Interface Electron complète

if [ “$1” = “–ui” ] || [ “$1” = “” ]; then
# Démarre le backend ET l’UI Electron
cd electron && npm start
fi

# Option 2 : Backend seul (pour tests)

if [ “$1” = “–backend-only” ]; then
cd backend && python3 main.py
fi

# Option 3 : UI dans navigateur (sans Electron)

if [ “$1” = “–browser” ]; then
# Démarre le backend en arrière-plan
cd backend && python3 main.py &
BACKEND_PID=$!
echo “Backend PID: $BACKEND_PID”

```
# Ouvre l'UI dans le navigateur
sleep 1
open frontend/index.html 2>/dev/null || \
xdg-open frontend/index.html 2>/dev/null || \
echo "Ouvrez manuellement: frontend/index.html"

# Attend Ctrl+C
trap "kill $BACKEND_PID" SIGINT SIGTERM
wait $BACKEND_PID
```

fi
