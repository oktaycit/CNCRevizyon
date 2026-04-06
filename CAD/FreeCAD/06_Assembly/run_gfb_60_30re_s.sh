#!/bin/bash
# GFB-60/30RE-S Model Başlatıcı Script
# FreeCAD CLI üzerinden modeli çalıştırır

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODEL_SCRIPT="${SCRIPT_DIR}/GFB_60_30RE_S_Model.py"

# FreeCAD yolunu kontrol et
FREECAD_CMD=""

# macOS kontrolü
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS'ta FreeCAD.app içinde gelir
    if [ -d "/Applications/FreeCAD.app/Contents/MacOS" ]; then
        FREECAD_CMD="/Applications/FreeCAD.app/Contents/MacOS/FreeCAD"
    elif [ -d "/Applications/FreeCAD.app/Contents/MacOS/bin" ]; then
        FREECAD_CMD="/Applications/FreeCAD.app/Contents/MacOS/bin/FreeCAD"
    elif command -v FreeCAD &> /dev/null; then
        FREECAD_CMD="FreeCAD"
    fi
else
    # Linux
    if command -v FreeCAD &> /dev/null; then
        FREECAD_CMD="FreeCAD"
    elif command -v freecad &> /dev/null; then
        FREECAD_CMD="freecad"
    fi
fi

if [ -z "$FREECAD_CMD" ]; then
    echo "HATA: FreeCAD bulunamadı!"
    echo ""
    echo "FreeCAD kurulum yolları:"
    echo "  macOS: /Applications/FreeCAD.app"
    echo "  Linux: /usr/bin/freecad veya /usr/local/bin/freecad"
    echo ""
    echo "veya PATH değişkeninize FreeCAD ekleyin."
    exit 1
fi

echo "========================================"
echo "GFB-60/30RE-S Model Başlatılıyor"
echo "========================================"
echo "FreeCAD: $FREECAD_CMD"
echo "Model: $MODEL_SCRIPT"
echo "========================================"

# FreeCAD CLI modunda başlat
# -c: Python komutu çalıştır
# --single-instance: Tek instance olarak başlat
"$FREECAD_CMD" --single-instance -c "exec(open('${MODEL_SCRIPT}').read()); create_complete_machine()"

# Başarısız olursa alternatif yöntem
if [ $? -ne 0 ]; then
    echo ""
    echo "Alternatif yöntem deneniyor..."
    "$FREECAD_CMD" -c "import sys; sys.path.insert(0, '${SCRIPT_DIR}'); import GFB_60_30RE_S_Model; GFB_60_30RE_S_Model.create_complete_machine()"
fi