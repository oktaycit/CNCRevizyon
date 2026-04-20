#!/bin/bash
# LiSEC GFB 60/30RE-S Referans Görsel İndirme Scripti
# Kullanım: ./download_images.sh

echo "============================================================"
echo "LiSEC GFB 60/30RE-S REFERANS GÖRSEL İNDİRME"
echo "============================================================"

# Klasör yapısını oluştur
REF_DIR="/Users/oktaycit/Projeler/CNCRevizyon/CAD/Reference_Images"

echo ""
echo "📁 Klasör yapısı oluşturuluyor..."

mkdir -p "$REF_DIR"/{01_Overall,02_CuttingHead,03_Frame,04_LinearGuides,05_Motors,06_Electronics,07_Conveyor}

echo "   ✓ Klasörler oluşturuldu"

# Manuel arama için kaynaklar
echo ""
echo "🔍 Aşağıdaki kaynaklardan görsel indirebilirsiniz:"
echo ""
echo "1. Google Görseller:"
echo "   https://www.google.com/search?q=LiSEC+GFB+60+30RE&tbm=isch"
echo ""
echo "2. Bing Görseller:"
echo "   https://www.bing.com/images/search?q=LiSEC+GFB+glass+cutting"
echo ""
echo "3. YouTube (Video thumbnail'ları):"
echo "   https://www.youtube.com/results?search_query=LiSEC+GFB+cutting"
echo ""
echo "4. DirectIndustry:"
echo "   https://www.directindustry.com/industrial-supplier/lisec-glass-cutting-machine.html"
echo ""
echo "5. Alibaba (Benzer makineler):"
echo "   https://www.alibaba.com/showroom/glass-cutting-machine-cnc.html"
echo ""

# Arama anahtar kelimeleri
echo "📋 Arama Anahtar Kelimeleri:"
echo ""
echo "   • LiSEC GFB 60/30RE"
echo "   • LiSEC CNC cutting bridge"
echo "   • LiSEC vertical glass cutter"
echo "   • LiSEC laminated glass cutting"
echo "   • cam kesme makinesi dikey"
echo "   • CNC cam kesme köprüsü"
echo ""

echo "💡 İpucu: İndirdiğiniz görselleri ilgili klasörlere kaydedin:"
echo ""
echo "   01_Overall/      - Genel görünüm"
echo "   02_CuttingHead/  - Kesim kafası"
echo "   03_Frame/        - Şase"
echo "   04_LinearGuides/ - Lineer raylar"
echo "   05_Motors/       - Motorlar"
echo "   06_Electronics/  - Elektronik"
echo "   07_Conveyor/     - Konveyör"
echo ""
echo "============================================================"
