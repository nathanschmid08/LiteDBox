const { app, BrowserWindow, ipcMain } = require("electron");
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

  // Zuerst den Loadscreen laden
  win.loadFile("loadscreen.html");

  // Nach z.B. 3 Sekunden auf das Hauptfenster wechseln
  setTimeout(() => {
    win.loadFile("index.html");
  }, 6000);
}

// IPC zum Speichern von Daten
ipcMain.handle("save-data", async (_, content) => {
  fs.writeFileSync("data.json", JSON.stringify({ data: content }, null, 2));
});

app.whenReady().then(createWindow);
