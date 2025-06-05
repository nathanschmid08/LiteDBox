const { app, BrowserWindow, ipcMain, screen } = require("electron");
const fs = require("fs");
const path = require("path");

let win;

function createWindow() {
  win = new BrowserWindow({
    width: 800,
    height: 600,
    icon: path.join(__dirname, "ASSETS", "logo.icns"),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      preload: path.join(__dirname, "preload.js")
    }
  });

  // Erst Loadscreen anzeigen
  win.loadFile("loadscreen.html");

  // Nach 6 Sekunden das Fenster auf Bildschirmgröße setzen und index.html laden
  setTimeout(() => {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;
    win.setBounds({ x: 0, y: 0, width, height }); // normales Fenster in voller Bildschirmgröße
    win.loadFile("index.html");
  }, 6000);
}

// IPC zum Speichern
ipcMain.handle("save-data", async (_, content) => {
  fs.writeFileSync("data.json", JSON.stringify({ data: content }, null, 2));
});

app.whenReady().then(createWindow);