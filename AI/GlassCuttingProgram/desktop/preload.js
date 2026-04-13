'use strict';

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('desktopAPI', {
  saveFile: (options) => ipcRenderer.invoke('desktop-save-file', options),
  storageGet: (keys) => ipcRenderer.invoke('desktop-storage-get', keys),
  storageSet: (payload) => ipcRenderer.invoke('desktop-storage-set', payload),
  isDesktop: true,
  platform: process.platform
});
