#!/bin/bash
# AI Model Hızlı Başlangıç ve Test Scripti

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🤖 Alibaba Cloud Lite Plan - AI Model Yöneticisi"
echo "================================================"
echo ""

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Bağımlılık kontrolü
check_dependencies() {
    echo -e "${YELLOW}📦 Bağımlılıkları kontrol ediliyor...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 bulunamadı${NC}"
        exit 1
    fi
    
    # Gerekli paketleri kontrol et
    python3 -c "import aiohttp" 2>/dev/null || {
        echo -e "${YELLOW}⚠️  aiohttp yüklü değil, yükleniyor...${NC}"
        pip3 install aiohttp
    }
    
    echo -e "${GREEN}✅ Bağımlılıklar hazır${NC}"
    echo ""
}

# Model listesi
show_models() {
    echo -e "${GREEN}📋 Kullanılabilir Modeller:${NC}"
    echo ""
    echo "┌────────────────────────────┬────────────────────────────┬────────────┐"
    echo "│ Model ID                   │ Kullanım Alanı             │ Priority   │"
    echo "├────────────────────────────┼────────────────────────────┼────────────┤"
    echo "│ qwen3.5-plus               │ Genel sorular, hızlı       │ 1 (En yüksek) │"
    echo "│ qwen3-max-2026-01-23       │ Karmaşık analiz            │ 2          │"
    echo "│ qwen3-coder-plus           │ Kod yazma, debug           │ 3          │"
    echo "│ qwen3-coder-next           │ İleri düzey kod            │ 4          │"
    echo "│ glm-4.7                    │ Alternatif, validasyon     │ 5          │"
    echo "│ kimi-k2.5                  │ Dokümantasyon, uzun context│ 6          │"
    echo "└────────────────────────────┴────────────────────────────┴────────────┘"
    echo ""
}

# Hızlı test
run_quick_test() {
    echo -e "${YELLOW}🚀 Hızlı test çalıştırılıyor...${NC}"
    python3 quick_test.py --mode parallel
}

# Tek model testi
run_single_test() {
    echo -e "${YELLOW}📍 Tek model testi...${NC}"
    python3 quick_test.py --mode single
}

# Paralel test
run_parallel_test() {
    echo -e "${YELLOW}🚀 Paralel test (tüm modeller)...${NC}"
    python3 quick_test.py --mode parallel
}

# Kullanıcı prompt'u ile test
run_custom_test() {
    echo -e "${YELLOW}💬 Özel prompt testi...${NC}"
    read -p "Soru veya görevinizi girin: " PROMPT
    python3 quick_test.py --mode parallel --prompt "$PROMPT"
}

# Ana menü
show_menu() {
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║         AI MODEL YÖNETİCİSİ - Ana Menü                ║"
    echo "╠════════════════════════════════════════════════════════╣"
    echo "║  1. Model Listesini Göster                             ║"
    echo "║  2. Hızlı Test (Paralel)                               ║"
    echo "║  3. Tek Model Testi                                    ║"
    echo "║  4. Özel Prompt Testi                                  ║"
    echo "║  5. Komut Satırı Örneği                                ║"
    echo "║  6. Çıkış                                              ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""
}

# Komut satırı örnekleri
show_examples() {
    echo ""
    echo -e "${GREEN}📖 Komut Satırı Kullanım Örnekleri:${NC}"
    echo ""
    echo "1. Paralel sorgu (tüm modeller):"
    echo "   python3 ai_orchestrator.py --mode parallel --prompt \"Servo alarm nasıl çözülür?\""
    echo ""
    echo "2. Tek model kullanımı:"
    echo "   python3 ai_orchestrator.py --mode single --models qwen3-coder-plus --prompt \"PID fonksiyonu yaz\""
    echo ""
    echo "3. Karşılaştırma tablosu:"
    echo "   python3 ai_orchestrator.py --mode aggregate --aggregate-method compare --prompt \"EtherCAT analizi\""
    echo ""
    echo "4. Voting (en iyi yanıt):"
    echo "   python3 ai_orchestrator.py --mode voting --prompt \"Optimizasyon önerisi\""
    echo ""
    echo "5. Cline MCP Tools (VS Code):"
    echo "   /ai_ask_parallel question=\"Soru\""
    echo "   /ai_code task=\"Kod görevi\" language=\"python\""
    echo "   /ai_debug error_code=\"AL013\" axis=\"X\""
    echo ""
}

# Ana döngü
main() {
    check_dependencies
    
    while true; do
        show_menu
        read -p "Seçiminiz (1-6): " choice
        
        case $choice in
            1)
                show_models
                ;;
            2)
                run_quick_test
                ;;
            3)
                run_single_test
                ;;
            4)
                run_custom_test
                ;;
            5)
                show_examples
                ;;
            6)
                echo -e "${GREEN}👋 Hoşçakalın!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}❌ Geçersiz seçim${NC}"
                ;;
        esac
        
        echo ""
        read -p "Devam etmek için Enter'a basın..." -n 1 -r
        echo ""
    done
}

# Script başlat
main
