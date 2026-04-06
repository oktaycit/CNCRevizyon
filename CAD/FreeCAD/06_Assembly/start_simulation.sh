#!/bin/bash
# GFB-60/30RE-S Simülasyon Başlatıcı
# FreeCAD GUI'yi açar ve doğru model scripti ile kullanım bilgisini verir

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_SCRIPT="${SCRIPT_DIR}/GFB_60_30RE_S_Model.py"
FREECAD_APP="/Applications/FreeCAD.app"

echo "========================================"
echo "GFB-60/30RE-S Simülasyon Başlatıcı"
echo "========================================"
echo ""

# FreeCAD'in kurulu olup olmadığını kontrol et
if [ ! -d "$FREECAD_APP" ] && ! command -v FreeCAD >/dev/null 2>&1; then
    echo "HATA: FreeCAD bulunamadı!"
    echo "FreeCAD uygulaması /Applications dizininde olmalıdır."
    exit 1
fi

echo "FreeCAD başlatılıyor..."
echo ""
echo "FreeCAD açıldığında, Python konsolunu açın (View → Panels → Python Console)"
echo "ve aşağıdaki komutu çalıştırın:"
echo ""
echo "  exec(open('${MODEL_SCRIPT}').read())"
echo "  create_complete_machine()"
echo ""
echo "Lamine kesim simülasyonu için:"
echo "  run_lamine_cutting_simulation(App.ActiveDocument, MachineParameters(), 30)"
echo ""
echo "========================================"
echo ""

# FreeCAD'i GUI olarak başlat
if [ -d "$FREECAD_APP" ]; then
    open -a "$FREECAD_APP"
else
    FreeCAD &
fi

# Kullanıcıya bilgi ver
echo "FreeCAD açılıyor..."
echo ""
echo "NOT: macOS güvenlik ayarları nedeniyle otomatik komut gönderimi"
echo "     engellenmiştir. Lütfen yukarıdaki komutları FreeCAD Python"
echo "     konsoluna manuel olarak girin."
echo ""

exit 0
