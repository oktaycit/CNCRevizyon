# GlassCutting Pro Desktop

Bu klasör, mevcut `web/app.html` arayüzünü Chrome olmadan çalışan masaüstü uygulamaya dönüştüren Electron kabuğunu içerir.

## Çalıştırma

```bash
cd AI/GlassCuttingProgram/desktop
npm install
npm start
```

## Ne Sağlar

- Chrome extension gerektirmez
- Ayrı masaüstü pencere
- Yerel ayar saklama
- G-code dosyasını masaüstü kaydetme diyaloğuyla kaydetme

## Mimari

- `main.js`: Electron ana process
- `preload.js`: güvenli renderer köprüsü
- UI: `../web/app.html`, `../web/app.js`, `../web/app.css`
