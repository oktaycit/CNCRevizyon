/**
 * GlassCutting Chrome App - Background Script
 * 
 * Bu script Chrome App olarak çalıştığında ana pencereyi açar.
 * Browser bağımsız, tam ekran uygulama olarak çalışır.
 */

chrome.app.runtime.onLaunched.addListener(() => {
  chrome.app.window.create('popup/popup.html', {
    id: 'glasscutting-main',
    bounds: {
      width: 1024,
      height: 768,
      left: 100,
      top: 100
    },
    minWidth: 800,
    minHeight: 600,
    frame: 'chrome',
    resizable: true,
    alwaysOnTop: false
  }, (createdWindow) => {
    console.log('GlassCutting App başlatıldı');
    
    // Pencere kapatıldığında cleanup
    createdWindow.onClosed.addListener(() => {
      console.log('GlassCutting App kapatıldı');
    });
  });
});

// App yüklendiğinde çalış
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('GlassCutting App yüklendi');
  } else if (details.reason === 'update') {
    console.log(`GlassCutting App güncellendi: ${details.previousVersion} -> ${chrome.runtime.getManifest().version}`);
  }
});

// Mesaj dinleyicisi
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Mesaj alındı:', message);
  
  if (message.action === 'getAppInfo') {
    sendResponse({
      name: chrome.runtime.getManifest().name,
      version: chrome.runtime.getManifest().version,
      isApp: true
    });
  }
  
  return true;
});
