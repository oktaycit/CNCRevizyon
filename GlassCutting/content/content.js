// GlassCutting - Content Script
// Web sayfaları ile entegrasyon

(function() {
  'use strict';

  console.log('[GlassCutting] Content script loaded');

  // ==================== G-KOD DOSYA ALGILAMA ====================
  detectGCodeFiles();

  // ==================== CONTEXT MENU ====================
  addContextMenu();

  // ==================== DRAG & DROP ====================
  setupDragAndDrop();

  // ==================== G-KOD DOSYA ALGILAMA ====================
  function detectGCodeFiles() {
    // Sayfadaki G-kod dosya linklerini algıla
    const gcodeLinks = document.querySelectorAll('a[href*=".nc"], a[href*=".gcode"], a[href*=".ngc"], a[href*=".txt"]');
    
    gcodeLinks.forEach(link => {
      // İkon ekle
      const icon = document.createElement('span');
      icon.innerHTML = ' 🔧';
      icon.style.cssText = 'margin-left: 4px; font-size: 12px;';
      link.appendChild(icon);

      // Tooltip ekle
      link.title = 'GlassCutting ile aç';
    });
  }

  // ==================== CONTEXT MENU ====================
  function addContextMenu() {
    // Sağ tık menüsüne "GlassCutting ile aç" seçeneği ekle
    document.addEventListener('contextmenu', (e) => {
      const existingMenu = document.getElementById('glasscutting-context-menu');
      if (existingMenu) {
        existingMenu.remove();
      }

      // Link üzerinde sağ tık
      if (e.target.tagName === 'A') {
        const menu = createContextMenu(e);
        document.body.appendChild(menu);
      }
    });

    // Menü dışına tıklayınca kapat
    document.addEventListener('click', () => {
      const existingMenu = document.getElementById('glasscutting-context-menu');
      if (existingMenu) {
        existingMenu.remove();
      }
    });
  }

  function createContextMenu(e) {
    const menu = document.createElement('div');
    menu.id = 'glasscutting-context-menu';
    menu.style.cssText = `
      position: fixed;
      top: ${e.clientY}px;
      left: ${e.clientX}px;
      background: white;
      border: 1px solid #ccc;
      border-radius: 4px;
      box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
      z-index: 10000;
      min-width: 150px;
    `;

    const item = document.createElement('div');
    item.textContent = '🔧 GlassCutting ile aç';
    item.style.cssText = `
      padding: 8px 12px;
      cursor: pointer;
      font-size: 13px;
    `;
    item.addEventListener('mouseover', () => {
      item.style.background = '#1976D2';
      item.style.color = 'white';
    });
    item.addEventListener('mouseout', () => {
      item.style.background = 'white';
      item.style.color = 'black';
    });
    item.addEventListener('click', () => {
      const link = e.target.closest('a');
      if (link) {
        loadGCodeFromUrl(link.href);
      }
    });

    menu.appendChild(item);
    return menu;
  }

  function loadGCodeFromUrl(url) {
    // Background'a URL'yi gönder
    chrome.runtime.sendMessage({
      action: 'loadGCodeFromUrl',
      url: url
    }, (response) => {
      console.log('[GlassCutting] Load response:', response);
    });
  }

  // ==================== DRAG & DROP ====================
  function setupDragAndDrop() {
    document.addEventListener('dragover', (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'copy';
    });

    document.addEventListener('drop', (e) => {
      e.preventDefault();
      
      const files = e.dataTransfer.files;
      if (files.length > 0) {
        handleDroppedFile(files[0]);
      }
    });
  }

  function handleDroppedFile(file) {
    const validExtensions = ['.nc', '.gcode', '.ngc', '.txt'];
    const fileExt = '.' + file.name.split('.').pop().toLowerCase();
    
    if (validExtensions.includes(fileExt)) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const gcode = event.target.result;
        
        // Popup'a dosya içeriğini gönder
        chrome.runtime.sendMessage({
          action: 'loadGCodeContent',
          content: gcode,
          filename: file.name
        }, (response) => {
          console.log('[GlassCutting] File loaded:', file.name);
          
          // Kullanıcıya bildirim göster
          showDropNotification(file.name);
        });
      };
      reader.readAsText(file);
    }
  }

  function showDropNotification(filename) {
    // Bildirim banner'ı göster
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #388E3C;
      color: white;
      padding: 12px 24px;
      border-radius: 4px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      z-index: 10001;
      font-size: 14px;
      animation: slideIn 0.3s ease;
    `;
    notification.textContent = `✓ ${filename} GlassCutting'e yüklendi`;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transition = 'opacity 0.3s';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }

  // ==================== KEYBOARD SHORTCUTS ====================
  document.addEventListener('keydown', (e) => {
    // Ctrl+Shift+G - GlassCutting'i aç
    if (e.ctrlKey && e.shiftKey && e.key === 'G') {
      e.preventDefault();
      chrome.runtime.sendMessage({ action: 'openPopup' });
    }
  });

  // ==================== SAYFA DEĞİŞİKLİĞİ ====================
  // SPA uygulamaları için sayfa değişimini algıla
  let lastUrl = location.href;
  const observer = new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      console.log('[GlassCutting] URL changed:', lastUrl);
      detectGCodeFiles();
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  console.log('[GlassCutting] Content script initialized');
})();
