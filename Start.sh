#!/bin/bash

# Start.sh — JARVIS

clear
echo “==================================”
echo “   JARVIS — Assistant IA Desktop  “
echo “==================================”
echo “”

# Vérifie Python

if ! command -v python3 &>/dev/null; then
echo “ERREUR: Python 3 requis”
echo “Installez-le sur https://python.org”
exit 1
fi

echo “Installation des dependances Python…”
pip3 install fastapi uvicorn sounddevice numpy pyttsx3 httpx psutil websockets

echo “”
echo “Demarrage du backend JARVIS…”
echo “”

python3 Main.py
