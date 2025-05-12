const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  saveData: (content) => ipcRenderer.invoke("save-data", content)
});
