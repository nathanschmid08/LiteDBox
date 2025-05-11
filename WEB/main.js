const { app, BrowserWindow, ipcMain } = require("electron");
const fs = require("fs");
const path = require("path");

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, "preload.js")
    }
  });

  win.loadFile("index.html");
}

ipcMain.handle("save-data", async (_, content) => {
  fs.writeFileSync("data.json", JSON.stringify({ data: content }, null, 2));
});

app.whenReady().then(createWindow);