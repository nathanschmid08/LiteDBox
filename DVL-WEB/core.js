const fs = require('fs');
const path = require('path');
const os = require('os');

window.onload = () => {
  const desktopPath = path.join(os.homedir(), 'Desktop');
  const folderPath = path.join(desktopPath, 'LiteDBox-Data');

  if (!fs.existsSync(folderPath)) {
    fs.mkdirSync(folderPath);
    console.log('Ordner LiteDBox-Data wurde erstellt.');
  } else {
    console.log('Ordner existiert bereits.');
  }
};