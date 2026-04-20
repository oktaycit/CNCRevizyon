#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiSEC GFB 60/30RE-S Referans Görsel İndirme Scripti

Bu script, LiSEC GFB cam kesme makinesi için referans görselleri
internet üzerinden indirip proje klasörüne kaydeder.

Kullanım:
    python download_reference_images.py
"""

import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Proje kök dizini
PROJECT_ROOT = Path("/Users/oktaycit/Projeler/CNCRevizyon")
REFERENCE_DIR = PROJECT_ROOT / "CAD" / "Reference_Images"

# Görsel kategorileri
CATEGORIES = {
    "01_Overall": "Genel makine görünümü",
    "02_CuttingHead": "Kesim kafası detayları",
    "03_Frame": "Şase ve konstrüksiyon",
    "04_LinearGuides": "Lineer kılavuzlar",
    "05_Motors": "Motorlar ve aktarma organları",
    "06_Electronics": "Elektronik ve kontrol",
    "07_Conveyor": "Konveyör sistemi",
}

# Referans görsel URL'leri (manuel olarak güncelleyin)
# Not: Gerçek URL'leri web'den bulduktan sonra buraya ekleyin
IMAGE_URLS = {
    "01_Overall": [
        # Örnek URL'ler - gerçer URL'leri web'den bulduktan sonra güncelleyin
        # "https://example.com/lisec-gfb-overview.jpg",
        # "https://example.com/lisec-gfb-isometric.jpg",
    ],
    "02_CuttingHead": [
        # "https://example.com/cutting-head-upper.jpg",
        # "https://example.com/cutting-head-lower.jpg",
    ],
    "03_Frame": [
        # "https://example.com/frame-structure.jpg",
    ],
    "04_LinearGuides": [
        # "https://example.com/hiwin-linear-guide.jpg",
    ],
    "05_Motors": [
        # "https://example.com/servo-motor.jpg",
    ],
    "06_Electronics": [
        # "https://example.com/control-panel.jpg",
    ],
    "07_Conveyor": [
        # "https://example.com/conveyor-system.jpg",
    ],
}

# Alternatif arama kaynakları
SEARCH_URLS = [
    "https://www.google.com/search?q=LiSEC+GFB+60+30RE+glass+cutting+machine&tbm=isch",
    "https://www.bing.com/images/search?q=LiSEC+GFB+glass+cutting",
    "https://www.youtube.com/results?search_query=LiSEC+GFB+cutting+machine",
    "https://www.directindustry.com/industrial-supplier/lisec-glass-cutting-machine.html",
]


def create_directory_structure():
    """Klasör yapısını oluştur"""
    print("📁 Klasör yapısı oluşturuluyor...")
    
    for category in CATEGORIES.keys():
        category_dir = REFERENCE_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {category}/")
    
    # README dosyası kontrolü
    readme_file = REFERENCE_DIR / "README.md"
    if not readme_file.exists():
        print("   ⚠️ README.md bulunamadı, oluşturuluyor...")
        create_readme()
    
    print(f"\n✅ Klasör yapısı hazır: {REFERENCE_DIR}")


def create_readme():
    """README dosyası oluştur"""
    readme_content = """# LiSEC GFB 60/30RE-S Referans Görseller

Bu klasör, LiSEC GFB 60/30RE-S cam kesme makinesi için referans görselleri içerir.

## Klasör Yapısı

- **01_Overall/** - Genel makine görünümü (izometrik, ön, yan, üst)
- **02_CuttingHead/** - Kesim kafası detayları (üst kafa, alt kafa, Z ekseni)
- **03_Frame/** - Şase ve konstrüksiyon detayları
- **04_LinearGuides/** - Lineer kılavuzlar ve raylar
- **05_Motors/** - Servo motorlar ve aktarma organları
- **06_Electronics/** - Elektronik kabinet, kontrol paneli, sensörler
- **07_Conveyor/** - Konveyör sistemi ve cam destek profilleri

## Görsel Ekleme

1. Web'den görselleri indirin
2. İlgili kategori klasörüne kaydedin
3. Dosya adlarını açıklayıcı şekilde verin (örn: `isometric_view.jpg`)

## Arama Kaynakları

- Google Görseller: https://www.google.com/search?q=LiSEC+GFB+60+30RE&tbm=isch
- Bing Görseller: https://www.bing.com/images/search?q=LiSEC+GFB+glass+cutting
- YouTube: https://www.youtube.com/results?search_query=LiSEC+GFB+cutting
- DirectIndustry: https://www.directindustry.com/

## Notlar

- Görseller telif hakkına tabi olabilir
- Sadece referans amaçlı kullanın
- Yüksek çözünürlüklü görseller tercih edin
"""
    
    readme_file = REFERENCE_DIR / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)


def download_image(url, category, filename=None):
    """Tek görsel indir"""
    try:
        # Kategori klasörünü al
        category_dir = REFERENCE_DIR / category
        
        # Dosya adını belirle
        if filename is None:
            filename = url.split('/')[-1].split('?')[0]
            if not filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                filename = f"image_{len(os.listdir(category_dir)) + 1}.jpg"
        
        # Hedef yol
        target_path = category_dir / filename
        
        # User-Agent başlığı
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # İndirme işlemi
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            with open(target_path, 'wb') as out_file:
                out_file.write(response.read())
        
        print(f"   ✓ İndirildi: {target_path.name}")
        return True
        
    except urllib.error.HTTPError as e:
        print(f"   ✗ HTTP Hatası ({e.code}): {url}")
        return False
    except urllib.error.URLError as e:
        print(f"   ✗ URL Hatası ({e.reason}): {url}")
        return False
    except Exception as e:
        print(f"   ✗ Beklenmeyen hata ({e}): {url}")
        return False


def download_all_images():
    """Tüm görselleri indir"""
    print("\n📥 Görseller indiriliyor...\n")
    
    total_downloaded = 0
    total_failed = 0
    
    for category, urls in IMAGE_URLS.items():
        if urls:
            print(f"\n{CATEGORIES[category]} ({category}/)")
            print("-" * 40)
            
            for url in urls:
                if download_image(url, category):
                    total_downloaded += 1
                else:
                    total_failed += 1
    
    print("\n" + "=" * 40)
    print(f"✅ Başarılı: {total_downloaded} görsel")
    print(f"❌ Başarısız: {total_failed} görsel")
    print("=" * 40)


def print_search_guide():
    """Arama rehberi yazdır"""
    print("\n🔍 Görsel Arama Rehberi\n")
    print("Aşağıdaki arama motorlarını kullanabilirsiniz:\n")
    
    for i, url in enumerate(SEARCH_URLS, 1):
        print(f"{i}. {url}")
    
    print("\n📋 Arama Anahtar Kelimeleri:\n")
    keywords = [
        "LiSEC GFB 60/30RE",
        "LiSEC CNC cutting bridge",
        "LiSEC vertical glass cutter",
        "LiSEC laminated glass cutting",
        "cam kesme makinesi dikey",
        "CNC cam kesme köprüsü",
        "glass cutting gantry",
    ]
    
    for keyword in keywords:
        print(f"   • {keyword}")
    
    print("\n💡 İpucu: Video thumbnail'lerinden de faydalanabilirsiniz")
    print("   YouTube'da 'LiSEC GFB' araması yapıp video'lardan ekran görüntüsü alabilirsiniz\n")


def main():
    """Ana fonksiyon"""
    print("=" * 60)
    print("LiSEC GFB 60/30RE-S REFERANS GÖRSEL İNDİRME")
    print("=" * 60)
    
    # Klasör yapısını oluştur
    create_directory_structure()
    
    # URL listesi boşsa rehberi göster
    has_urls = any(urls for urls in IMAGE_URLS.values())
    
    if not has_urls:
        print("\n⚠️  Henüz görsel URL'si eklenmemiş!")
        print("\nİki seçeneğiniz var:\n")
        print("1. **Manuel İndirme:**")
        print("   - Yukarıdaki arama kaynaklarını kullanın")
        print("   - Görselleri ilgili klasörlere kaydedin\n")
        print("2. **Script ile İndirme:**")
        print("   - `IMAGE_URLS` sözlüğüne URL'leri ekleyin")
        print("   - Script'i tekrar çalıştırın\n")
        
        print_search_guide()
        
        # Örnek URL ekleme formatı
        print("\n📝 Örnek URL Ekleme Formatı:\n")
        print("IMAGE_URLS = {")
        print('    "01_Overall": [')
        print('        "https://ornek.com/lisec-gfb-genel.jpg",')
        print('        "https://ornek.com/lisec-gfb-on.jpg",')
        print('    ],')
        print('    "02_CuttingHead": [')
        print('        "https://ornek.com/cutting-head-upper.jpg",')
        print('    ],')
        print("}")
        print()
    else:
        # Görselleri indir
        download_all_images()
        print("\n✅ İşlem tamamlandı!")
        print(f"📂 Görseller: {REFERENCE_DIR}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
