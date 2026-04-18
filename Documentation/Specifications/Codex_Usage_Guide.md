# Codex Kullanım Kılavuzu

Bu doküman, `CNCRevizyon` projesinde Codex'i daha verimli, güvenli ve tekrar kullanılabilir şekilde kullanmak için hazırlanmıştır.

## Amaç

Bu projede Codex'i en iyi şu işlerde kullanabilirsiniz:

- Python modüllerini inceleme, düzeltme ve geliştirme
- FreeCAD scriptleri üretme veya revize etme
- G-code üretim akışını analiz etme
- Simülasyon ve test senaryoları ekleme
- Dokümantasyonları standardize etme
- Elektrik, CAD ve yazılım çıktıları arasında tutarsızlık bulma

## Temel Prensipler

İyi sonuç almak için prompt'larda şu dört unsur mümkün olduğunca açık olmalıdır:

1. Kapsam
2. Hedef çıktı
3. Kısıtlar
4. Doğrulama beklentisi

Örnek yapı:

```text
Şu klasör veya dosyada çalış:
...

Hedef:
...

Kısıtlar:
...

Doğrulama:
...
```

## Hızlı Şablonlar

### 1. Kod İnceleme

```text
/Users/oktaycit/Projeler/CNCRevizyon/AI/GlassCuttingProgram/modules içinde ilgili dosyaları incele.
Öncelik sırasıyla bug, davranışsal regresyon, eksik test ve bakım risklerini bul.
Özet yerine önce bulguları ver.
Henüz kod değiştirme.
```

### 2. Hata Ayıklama

```text
/Users/oktaycit/Projeler/CNCRevizyon/AI/GlassCuttingProgram/modules/gcode_generator.py dosyasındaki hatayı incele.
Önce muhtemel kök nedenleri sırala.
Sonra en düşük riskli düzeltmeyi uygula.
Mümkünse ilgili test veya kısa doğrulama adımı ekle.
```

### 3. Güvenli Refactor

```text
/Users/oktaycit/Projeler/CNCRevizyon/AI/GlassCuttingProgram/modules içinde sadece ilgili dosyada refactor yap.
Davranışı değiştirme.
İsimlendirme, fonksiyon ayrıştırma ve okunabilirlik iyileştirmesi yap.
Değişiklik sonrası hangi davranışların korunduğunu açıkla.
```

### 4. Yeni Özellik Ekleme

```text
/Users/oktaycit/Projeler/CNCRevizyon/AI/GlassCuttingProgram içinde [özelliği] ekle.
Önce mevcut akışı oku ve entegrasyon noktasını belirle.
Mevcut dosya yapısını bozma.
Gerekirse küçük test veya örnek giriş/çıkış ekle.
```

### 5. Test Yazdırma

```text
/Users/oktaycit/Projeler/CNCRevizyon/AI/GlassCuttingProgram için hızlı çalışan testler ekle.
Önce mevcut test yaklaşımını incele.
En kritik iş kurallarını kapsayan küçük ama etkili testler yaz.
Gereksiz mock kullanımından kaçın.
```

### 6. G-code Akışı Analizi

```text
/Users/oktaycit/Projeler/CNCRevizyon/AI/GlassCuttingProgram/modules/gcode_generator.py ve ilişkili modülleri incele.
Sipariş verisinden nihai .nc çıktısına kadar akışı çıkar.
Riskli dönüşüm noktalarını ve olası veri kaybı alanlarını belirt.
Henüz değişiklik yapma.
```

### 7. FreeCAD Script Üretimi

```text
/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD altında mevcut stil ve isimlendirmeyi incele.
Sonra [parça adı] için yeni bir parametrik FreeCAD scripti hazırla.
Ölçüleri mm kabul et.
Çıktının mevcut klasör yapısına uyumlu olmasına dikkat et.
```

### 8. FreeCAD Script Düzeltme

```text
/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly içindeki scripti incele.
Amaç: hatalı geometri veya kırık referansları düzeltmek.
Mevcut parametrik yaklaşımı koru.
Değişiklikleri kısa teknik notlarla açıkla.
```

### 9. Mekanik Dokümantasyon Temizliği

```text
/Users/oktaycit/Projeler/CNCRevizyon/CAD ve /Users/oktaycit/Projeler/CNCRevizyon/Documentation/Specifications altındaki ilgili dosyaları incele.
Terminolojiyi standardize et.
Çelişen ölçü, isim veya parça tanımlarını listele.
Önce raporla, sonra istenirse düzelt.
```

### 10. Elektrik ve Yazılım Tutarlılık Kontrolü

```text
/Users/oktaycit/Projeler/CNCRevizyon/Electrical ve /Users/oktaycit/Projeler/CNCRevizyon/Firmware klasörlerini çapraz incele.
I/O isimleri, register mantığı ve sinyal yönlerinde tutarsızlık varsa bul.
Bulguları önem sırasına göre ver.
Kod değiştirme.
```

### 11. Simülatör Geliştirme

```text
/Users/oktaycit/Projeler/CNCRevizyon/Firmware/RaspberryPi/src/nc300_simulator.py üzerinde çalış.
Mevcut CLI davranışını bozma.
[istenen state machine veya register davranışını] ekle.
Mümkünse demo veya JSON çıktı üzerinden doğrulama yap.
```

### 12. Electron Masaüstü İyileştirme

```text
/Users/oktaycit/Projeler/CNCRevizyon/AI/GlassCuttingProgram/desktop ve ../web tarafını birlikte incele.
Amaç: masaüstü deneyimini iyileştirmek.
Kurulum ve çalışma akışını bozma.
Gerekirse README'yi de güncelle.
```

### 13. Dokümantasyon Üretimi

```text
/Users/oktaycit/Projeler/CNCRevizyon içindeki ilgili klasörü incele.
[konu] için kısa ama teknik bir README veya kullanım kılavuzu yaz.
Pazarlama dili kullanma.
Kurulum, kullanım, sınırlar ve dosya yapısı net olsun.
```

### 14. Teslim Öncesi Kontrol

```text
/Users/oktaycit/Projeler/CNCRevizyon/Delivery klasörünü ve kaynak dosyaları incele.
Teslim çıktılarının eksik, tutarsız veya eski olabilecek kısımlarını bul.
Bunu bir kontrol listesi halinde ver.
Henüz dosya silme veya taşıma yapma.
```

### 15. Büyük Görevlerde Aşamalı Çalışma

```text
Bu görevi 3 aşamada ele al:
1. İlgili dosyaları ve mevcut akışı incele
2. Kısa plan çıkar
3. Onaya ihtiyaç duymadan düşük riskli değişiklikleri uygula ve doğrula

Görev:
[buraya görev]
```

## Bu Repo İçin Hazır Prompt Örnekleri

### G-code güvenlik kontrolü

```text
/Users/oktaycit/Projeler/CNCRevizyon/AI/GlassCuttingProgram/modules/gcode_generator.py dosyasını incele.
Özellikle laminated kesim, header/footer ve NC300 uyumluluğu açısından riskli yerleri bul.
Bulguları önce ver, ardından en küçük güvenli düzeltmeyi uygula.
```

### FreeCAD montaj analizi

```text
/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly altındaki scriptleri okuyup montaj akışını çıkar.
Ana assembly bağımlılıklarını, eksik dosyaları ve kırılgan referansları belirt.
Henüz kod değiştirme.
```

### Simülatör davranış genişletme

```text
/Users/oktaycit/Projeler/CNCRevizyon/Firmware/RaspberryPi/src/nc300_simulator.py içinde lamine çevrim state machine davranışını incele.
Gerçek NC300'e daha yakın olacak şekilde eksik geçişleri tamamla.
Mevcut demo komutlarını bozma.
```

### Elektrik-dokümantasyon çapraz kontrolü

```text
/Users/oktaycit/Projeler/CNCRevizyon/Electrical/Schematics ve /Users/oktaycit/Projeler/CNCRevizyon/Documentation/Reports klasörlerini karşılaştır.
Aynı sinyal, cihaz veya modül için farklı isimlendirmeler varsa listele.
Önce sadece bulguları ver.
```

## İyi Prompt ve Zayıf Prompt Karşılaştırması

Zayıf:

```text
Bu projeyi düzelt.
```

İyi:

```text
/Users/oktaycit/Projeler/CNCRevizyon/AI/GlassCuttingProgram/modules/path_planner.py dosyasını incele.
Amaç: rota üretimindeki okunabilirliği artırmak ve olası köşe durumlarını güvenli hale getirmek.
Davranışı mümkün olduğunca koru.
Değişiklik sonrası hangi senaryoları kontrol ettiğini yaz.
```

Zayıf:

```text
FreeCAD kodu yaz.
```

İyi:

```text
/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD altındaki mevcut generator scriptlerini incele.
Aynı stile uygun şekilde kablo gland montaj braketi için parametrik bir script oluştur.
Ölçüler mm olsun, çıktı isimleri mevcut klasör yapısına uysun.
```

## Çalışma Tarzı Önerisi

Günlük kullanım için şu akış iyi çalışır:

1. Önce inceletin
2. Sonra plan çıkarttırın
3. Ardından küçük ve güvenli patch uygulatın
4. Mümkünse test veya doğrulama yaptırın
5. En sonda özet ve kalan riskleri alın

Örnek:

```text
Önce ilgili dosyaları incele.
Sonra kısa bir plan çıkar.
Ardından doğrudan değişikliği uygula.
Mümkünse test et.
Sonunda neyi değiştirdiğini ve kalan riskleri kısa yaz.
```

## Özellikle Belirtmeniz Faydalı Olan Kısıtlar

Prompt'lara duruma göre şunları ekleyin:

- "Henüz kod değiştirme"
- "Sadece şu dosyada çalış"
- "Davranışı bozma"
- "Önce bulguları ver"
- "Mevcut isimlendirme stilini koru"
- "Test yoksa küçük smoke test ekle"
- "README'yi de güncelle"
- "Teslim çıktılarıyla uyumlu kal"
- "Elektrik/CAD terimlerini standardize et"

## Ne Zaman Çok İyi Sonuç Verir

Codex bu projede en çok şu durumlarda değer üretir:

- Belirli klasör veya dosya verilmişse
- Başarı ölçütü netse
- Değişiklik sınırı belliyse
- Çıktı türü tanımlanmışsa
- "incele -> uygula -> doğrula" akışı istenmişse

## Ne Zaman Verim Düşer

Şu tür istemlerde sonuç kalitesi düşer:

- "Bir bakıver"
- "Projeyi geliştir"
- "Bunu hallet"
- "Daha iyi yap"

Bu tip geniş istemleri dosya yolu, hedef ve kısıt ekleyerek daraltmak gerekir.

## Kısa Komut Kalıbı

En pratik genel kalıp:

```text
[dosya/klasör]
incele,
[hedef]
uygula,
[kısıt]
koru,
mümkünse
[test/doğrulama]
yap,
sonunda kısa özet ver.
```

Örnek:

```text
/Users/oktaycit/Projeler/CNCRevizyon/AI/GlassCuttingProgram/modules/database.py dosyasını incele,
oturum yönetimini sadeleştir,
mevcut veri formatını koru,
mümkünse küçük bir doğrulama yap,
sonunda kısa özet ver.
```
