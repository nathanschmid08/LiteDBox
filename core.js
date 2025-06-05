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

  const folderListElem = document.getElementById('folderList');
  const fileListElem = document.getElementById('fileList');

  // Hilfsfunktion: Nur Ordner filtern
  function getFolders(source) {
    return fs.readdirSync(source, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory())
      .map(dirent => dirent.name);
  }

  // Hilfsfunktion: Nur Dateien filtern
  function getFiles(source) {
    return fs.readdirSync(source, { withFileTypes: true })
      .filter(dirent => dirent.isFile())
      .map(dirent => dirent.name);
  }

  // Ordner laden und in Sidebar anzeigen
  function loadFolders() {
    folderListElem.innerHTML = ''; // leeren
    const folders = getFolders(folderPath);

    if (folders.length === 0) {
      folderListElem.innerHTML = '<li><em>Keine Ordner gefunden</em></li>';
      fileListElem.innerHTML = '';
      return;
    }

    folders.forEach(folder => {
      const li = document.createElement('li');
      li.textContent = folder;
      li.style.userSelect = 'none';

      li.onclick = () => {
        loadFiles(folder);
      };

      folderListElem.appendChild(li);
    });

    fileListElem.innerHTML = '<li><em>Bitte Ordner auswählen</em></li>';
  }

  // Dateien des ausgewählten Ordners anzeigen
  function loadFiles(folderName) {
    fileListElem.innerHTML = ''; // leeren
    const selectedFolderPath = path.join(folderPath, folderName);

    let files;
    try {
      files = getFiles(selectedFolderPath);
    } catch (error) {
      files = [];
      console.error('Fehler beim Lesen der Dateien:', error);
    }

    if (files.length === 0) {
      fileListElem.innerHTML = '<li><em>Keine Dateien gefunden</em></li>';
      return;
    }

    files.forEach(file => {
      const li = document.createElement('li');
      li.textContent = file;
      li.style.userSelect = 'none';
      fileListElem.appendChild(li);
    });
  }

  // Lade beim Start die Ordner
  loadFolders();
};