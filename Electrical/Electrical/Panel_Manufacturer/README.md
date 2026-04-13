# GFB60-30RE-S Pano Imalat Belgeleri

**Teslim Paketi Index**

> Revizyon notu: `U2 / DOP-110CS` operator terminali ana pano uzerinde degil, koprunun home noktalarina yakin saha montajli uzak terminal olarak uygulanacaktir.

---

## Belgeler Listesi

| Dosya No | Dosya Adi | Aciklama | Format |
|----------|-----------|----------|--------|
| **00** | 00_TITLE_PAGE.md | Kapak sayfasi | Markdown |
| **01** | 01_PANEL_LAYOUT.md | Pano yerlesim plani | Markdown |
| **02** | 02_TERMINAL_DIAGRAMS.md | Klemens ve terminal strip semalari | Markdown |
| **03** | 03_CABLE_SCHEDULE.md | Kablo listesi ve uzunluklari | Markdown |
| **04** | 04_ASSEMBLY_NOTES.md | Montaj talimatlari | Markdown |
| **05** | GFB60-30RE-S_BOM.md | Malzeme listesi (BOM) | Markdown |
| **06** | TERMINAL_TO_TERMINAL_LIST.md | Terminal-terminal baglanti listesi | Markdown |
| **07** | WIRE_LIST_SAHA.md | Saha kablo listesi | Markdown |
| **App-A** | Schematics/ | Elektrik semasi (DrawIO) | .drawio / .pdf |

---

## Klasor Yapisi

```
Panel_Manufacturer/
|-- 00_TITLE_PAGE.md
|-- 01_PANEL_LAYOUT.md
|-- 02_TERMINAL_DIAGRAMS.md
|-- 03_CABLE_SCHEDULE.md
|-- 04_ASSEMBLY_NOTES.md
|-- README.md (Bu dosya)
|-- BOM/
|   |-- GFB60-30RE-S_BOM.md
|-- Wiring/
|   |-- TERMINAL_TO_TERMINAL_LIST.md
|   |-- WIRE_LIST_SAHA.md
|-- Schematics/
|   |-- GFB60_30RE_S_Electrical.drawio.pdf
|   |-- (DrawIO source files)
```

---

## Kullanım Talimati

### Pano Imalatci İcin

1. **00_TITLE_PAGE.md** - Proje ve belge bilgilerini kontrol edin
2. **01_PANEL_LAYOUT.md** - Pano boyutlarini ve bileşen yerlesimini uygulayın
3. **02_TERMINAL_DIAGRAMS.md** - Terminal strip konfigürasyonlarını uygulayın
4. **03_CABLE_SCHEDULE.md** - Kablo tiplerini ve uzunluklarini kullanın
5. **04_ASSEMBLY_NOTES.md** - Montaj sırasını ve test protokolünü izleyin
6. **BOM/** - Malzeme listesini kontrol edin, eksikleri bildirin
7. **Wiring/** - Baglanti listesini kablolama için kullanın
8. **Schematics/** - Elektrik semasını referans olarak kullanın

### Test ve Teslim

- **04_ASSEMBLY_NOTES.md** içindeki Test Protokolünü uygulayın
- Test raporu hazırlayın
- Tüm belgelerle birlikte teslim edin

---

## İletişim

**Tasarimci:** CNCRevizyon Projesi
**Tarih:** 12.04.2026
**Revizyon:** 4.2

---

## Degisiklik Talebi

Belgelerde degisiklik gerekiyorsa:
1. Tasarimci ile iletisime gecin
2. Degisiklik talebi belgesi hazırlayın
3. Revizyon numarasini guncelleyin
