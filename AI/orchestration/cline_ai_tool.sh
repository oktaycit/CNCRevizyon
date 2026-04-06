#!/bin/bash
# Cline AI Tool - Shell Wrapper
# Bu script, Cline'ın AI modellerini kullanması için basit bir arayüz sağlar

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Varsayılan değerler
TASK="${1:-code}"
CUSTOM="${2:-}"

# Kullanım bilgisi
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    echo "CNC AI Orchestrator - Cline Tool"
    echo ""
    echo "Kullanım: $0 [task] [custom_soru]"
    echo ""
    echo "Task tipleri:"
    echo "  code     - Kod yazdır (Python/FreeCAD/G-code)"
    echo "  design   - Tasarım önerisi"
    echo "  optimize - Optimizasyon"
    echo "  debug    - Hata ayıklama"
    echo "  plc      - PLC/EtherCAT"
    echo "  cam      - E-Cam profili"
    echo "  gcode    - G-kod programı"
    echo "  safety   - Güvenlik analizi"
    echo ""
    echo "Örnekler:"
    echo "  $0 code 'X ekseni limit switch fonksiyonu'"
    echo "  $0 debug 'Err 13.1 position deviation'"
    exit 0
fi

# Demo task seçimi (custom yoksa)
if [[ -z "$CUSTOM" ]]; then
    case "$TASK" in
        code) CUSTOM="X ekseni için limit switch kontrolü yapan Python fonksiyonu yaz" ;;
        design) CUSTOM="Kesim kafası için motor montaj brakti tasarımı öner" ;;
        optimize) CUSTOM="6000x3000mm camdan 500x400mm parçalar için optimal yerleşim" ;;
        debug) CUSTOM="X ekseni servo alarmı: Err 13.1 (Position deviation too large)" ;;
        plc) CUSTOM="R1-EC0902D input modülü için EtherCAT PDO mapping" ;;
        cam) CUSTOM="12mm lamine cam için E-Cam profili oluştur" ;;
        gcode) CUSTOM="500x400x12mm cam için dikdörtgen kesim programı" ;;
        safety) CUSTOM="STO devresi için ISO 13849-1 PL d analizi" ;;
        *) CUSTOM="Genel soru" ;;
    esac
fi

echo "=============================================="
echo "CNC AI Orchestrator - Cline Tool"
echo "=============================================="
echo "Task: $TASK"
echo "Soru: $CUSTOM"
echo "=============================================="
echo ""

# Python script'ini çalıştır (Python 3.14 ile)
python3.14 cnc_orchestrator.py --task "$TASK" --custom "$CUSTOM" --mode specialized
