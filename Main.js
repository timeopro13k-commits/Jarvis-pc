// electron/main.js
/**

- Process principal Electron.
- Configure la fenêtre en overlay transparent, toujours au premier plan.
  */

const { app, BrowserWindow, Tray, Menu, nativeImage, ipcMain } = require(‘electron’);
const path = require(‘path’);
const { spawn } = require(‘child_process’);

let mainWindow = null;
let tray = null;
let backendProcess = null;

// ── Fenêtre principale ────────────────────────────────────────────────────────
function createWindow() {
mainWindow = new BrowserWindow({
width: 900,
height: 700,

```
// Mode overlay : transparent, pas de frame
transparent: true,
frame: false,

// Toujours au dessus des autres fenêtres
alwaysOnTop: true,

// Centré sur l'écran
center: true,

// Permet le clic à travers les zones transparentes
// (désactivé pour pouvoir interagir avec l'input)
// setIgnoreMouseEvents(true, { forward: true })

webPreferences: {
  preload: path.join(__dirname, 'preload.js'),
  nodeIntegration: false,
  contextIsolation: true,
},

// Pas dans la barre des tâches
skipTaskbar: false,

// Titre
title: 'JARVIS',

// Icône
// icon: path.join(__dirname, 'assets/icon.png'),

// Vibrancy (macOS) - effet verre
vibrancy: 'ultra-dark',
visualEffectState: 'active',

// Rounded corners (macOS)
roundedCorners: true,
```

});

// Charge l’UI
mainWindow.loadFile(path.join(__dirname, ‘../frontend/index.html’));

// Ouvre DevTools en dev
if (process.argv.includes(’–dev’)) {
mainWindow.webContents.openDevTools({ mode: ‘detach’ });
}

// Gestion de la fermeture : masquer plutôt que quitter
mainWindow.on(‘close’, (e) => {
if (!app.isQuitting) {
e.preventDefault();
mainWindow.hide();
}
});

mainWindow.on(‘closed’, () => { mainWindow = null; });
}

// ── System Tray ───────────────────────────────────────────────────────────────
function createTray() {
// Icône simple (16x16 blanc)
const icon = nativeImage.createEmpty();
tray = new Tray(icon);

const menu = Menu.buildFromTemplate([
{ label: ‘JARVIS v1.0’, enabled: false },
{ type: ‘separator’ },
{ label: ‘Afficher / Masquer’, click: toggleWindow },
{ label: ‘Paramètres’, click: openSettings },
{ type: ‘separator’ },
{ label: ‘Quitter’, click: quitApp },
]);

tray.setContextMenu(menu);
tray.setToolTip(‘JARVIS — Assistant IA’);
tray.on(‘click’, toggleWindow);
}

function toggleWindow() {
if (!mainWindow) return;
if (mainWindow.isVisible()) {
mainWindow.hide();
} else {
mainWindow.show();
mainWindow.focus();
}
}

function openSettings() {
// TODO: ouvrir une fenêtre de paramètres
}

function quitApp() {
app.isQuitting = true;
stopBackend();
app.quit();
}

// ── Backend Python ─────────────────────────────────────────────────────────────
function startBackend() {
const pythonScript = path.join(__dirname, ‘../backend/main.py’);
const python = process.platform === ‘win32’ ? ‘python’ : ‘python3’;

console.log(`Démarrage backend: ${python} ${pythonScript}`);

backendProcess = spawn(python, [pythonScript], {
stdio: [‘ignore’, ‘pipe’, ‘pipe’],
detached: false,
});

backendProcess.stdout.on(‘data’, (data) => {
process.stdout.write(`[Backend] ${data}`);
});

backendProcess.stderr.on(‘data’, (data) => {
process.stderr.write(`[Backend ERR] ${data}`);
});

backendProcess.on(‘close’, (code) => {
console.log(`Backend arrêté (code: ${code})`);
backendProcess = null;

```
// Redémarre si crash inattendu
if (code !== 0 && !app.isQuitting) {
  console.log('Redémarrage du backend dans 3s...');
  setTimeout(startBackend, 3000);
}
```

});

backendProcess.on(‘error’, (err) => {
console.error(‘Erreur backend:’, err.message);
// Continuer sans backend (mode démo)
});
}

function stopBackend() {
if (backendProcess) {
backendProcess.kill();
backendProcess = null;
}
}

// ── IPC handlers ──────────────────────────────────────────────────────────────
ipcMain.on(‘minimize’, () => mainWindow?.minimize());
ipcMain.on(‘hide’, () => mainWindow?.hide());
ipcMain.on(‘quit’, quitApp);

// ── Raccourci global ──────────────────────────────────────────────────────────
const { globalShortcut } = require(‘electron’);

function registerShortcuts() {
// Ctrl+Shift+J (ou Cmd+Shift+J sur Mac) pour afficher/masquer
const shortcut = process.platform === ‘darwin’ ? ‘Cmd+Shift+J’ : ‘Ctrl+Shift+J’;

const ok = globalShortcut.register(shortcut, toggleWindow);
if (!ok) console.warn(‘Raccourci global non enregistré’);
else console.log(`Raccourci: ${shortcut} → Afficher/Masquer JARVIS`);
}

// ── App lifecycle ─────────────────────────────────────────────────────────────
app.whenReady().then(() => {
createWindow();
// createTray(); // Décommenter pour activer la tray
registerShortcuts();

// Démarre le backend Python
startBackend();

app.on(‘activate’, () => {
if (!mainWindow) createWindow();
else mainWindow.show();
});
});

app.on(‘window-all-closed’, () => {
if (process.platform !== ‘darwin’) app.quit();
});

app.on(‘will-quit’, () => {
globalShortcut.unregisterAll();
stopBackend();
});

app.on(‘before-quit’, () => {
app.isQuitting = true;
});
