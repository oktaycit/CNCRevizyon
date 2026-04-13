#!/usr/bin/env node
'use strict';

const { app, BrowserWindow, dialog, ipcMain, shell } = require('electron');
const fs = require('fs');
const path = require('path');

const APP_TITLE = 'GlassCutting Pro';
const APP_STORAGE_FILE = 'desktop-storage.json';

let mainWindow = null;

function getStoragePath() {
  return path.join(app.getPath('userData'), APP_STORAGE_FILE);
}

function readStorage() {
  const storagePath = getStoragePath();
  if (!fs.existsSync(storagePath)) {
    return {};
  }

  try {
    return JSON.parse(fs.readFileSync(storagePath, 'utf8'));
  } catch (error) {
    console.error('[desktop] Failed to read storage:', error);
    return {};
  }
}

function writeStorage(data) {
  const storagePath = getStoragePath();
  fs.mkdirSync(path.dirname(storagePath), { recursive: true });
  fs.writeFileSync(storagePath, JSON.stringify(data, null, 2), 'utf8');
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 960,
    minWidth: 1100,
    minHeight: 720,
    title: APP_TITLE,
    autoHideMenuBar: true,
    backgroundColor: '#0d1b2a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  mainWindow.loadFile(path.join(__dirname, '..', 'web', 'app.html'));

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

ipcMain.handle('desktop-storage-get', async (_event, keys) => {
  const storage = readStorage();

  if (!keys) {
    return storage;
  }

  const keyList = Array.isArray(keys) ? keys : [keys];
  const result = {};
  for (const key of keyList) {
    result[key] = storage[key];
  }
  return result;
});

ipcMain.handle('desktop-storage-set', async (_event, payload) => {
  const storage = readStorage();
  const nextStorage = { ...storage, ...(payload || {}) };
  writeStorage(nextStorage);
  return true;
});

ipcMain.handle('desktop-save-file', async (_event, options) => {
  const {
    content = '',
    defaultPath = 'program.nc',
    filters = [{ name: 'NC Files', extensions: ['nc', 'gcode', 'ngc', 'txt'] }]
  } = options || {};

  const result = await dialog.showSaveDialog({
    title: 'Save G-code',
    defaultPath,
    filters
  });

  if (result.canceled || !result.filePath) {
    return { canceled: true };
  }

  fs.writeFileSync(result.filePath, content, 'utf8');
  return { canceled: false, filePath: result.filePath };
});

app.whenReady().then(() => {
  createMainWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
