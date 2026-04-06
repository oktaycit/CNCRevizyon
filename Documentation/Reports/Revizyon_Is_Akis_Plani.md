# GFB-60/30RE-S Revizyon Is Akis Plani

**Tarih:** 06.04.2026
**Kapsam:** Mekanik, elektrik, otomasyon, test ve devreye alma
**Amac:** Revizyonu kontrol edilebilir adimlarla ilerletmek, disiplinler arasi bagimliliklari netlestirmek ve sahada tekrar is yapma riskini azaltmak.

---

## 1. Genel Yaklasim

Revizyon su ana fazlarla yurutilmelidir:

1. Mevcut durum tespiti ve gereksinimlerin dondurulmasi
2. Tasarim dogrulama ve revizyon kararlarinin netlestirilmesi
3. Mekanik ve elektrik detaylandirma
4. Yazilim ve kontrol altyapisinin olusturulmasi
5. Atolye montaj ve panel uygulamasi
6. I/O, hareket ve guvenlik testleri
7. Proses testleri ve kabul
8. Dokumantasyon kapama ve devir

---

## 2. Faz Bazli Is Akisi

## Faz 1: Mevcut Durum Tespiti

**Hedef:** Makinenin mevcut mekanik, elektrik ve proses durumunu kesinlestirmek.

**Yapilacaklar**
- Orijinal makine uzerinde eksenler, sensorler, valfler, kablolama ve pano envanteri cikarilir.
- Duz cam ve lamine modulu icin mevcut fonksiyonlar ayri ayri listelenir.
- Kritik olculer, montaj yuzeyleri, baglanti noktalari ve mevcut mekanik kisitlar kayit altina alinir.
- Mevcut I/O noktalarinin sahadaki karsiliklari tablo haline getirilir.
- Revizyon kapsam disi kalacak ekipmanlar netlestirilir.

**Ciktilar**
- Mevcut durum raporu
- I/O envanter listesi
- Mekanik olcu ve referans seti
- Risk ve eksik veri listesi

**Tamamlanma Kriteri**
- Tasarim ekibi, elektrik ekibi ve yazilim ekibi ayni saha referans seti ile calisiyor olmali.

## Faz 2: Gereksinim Dondurma ve Mimari Onay

**Hedef:** Revizyonun teknik sinirlarini degistirmeden ilerleyebilmek.

**Yapilacaklar**
- Nihai eksen listesi X, Y, Z, C, V olarak onaylanir.
- Servo motor ve surucu secimleri son kez kontrol edilir.
- R1-EC genisleme mimarisi ve toplam I/O sayisi kesinlestirilir.
- STO, emniyet zinciri ve acil stop mimarisi onaylanir.
- Lamine kesim sureci icin isitma, alt kesim, ayirma ve kirma adimlari netlestirilir.

**Ciktilar**
- Onayli sistem mimarisi
- Onayli ekipman listesi
- Onayli I/O adresleme mantigi
- Fonksiyon listesi ve operasyon senaryolari

**Tamamlanma Kriteri**
- Yeni ekipman secimi veya adres yapisi sahaya inmeden degistirilmeyecek seviyede netlesmeli.

## Faz 3: Mekanik Revizyon Tasarimi

**Hedef:** Tum montajlarin ve hareketli yapilarin imalata hazir hale gelmesi.

**Yapilacaklar**
- FreeCAD tarafinda motorlar, lineer raylar, kesim kafasi ve elektronik kutular tamamlanir.
- VB-Modul icin V ekseni hareket yapisi ve ust-alt kesim offset mantigi modellenir.
- Sensor braketleri, R1-EC kutu yerlestirmesi ve kablo tasima guzergahlari tasarlanir.
- Ana montaj simule edilerek cakisma kontrolu yapilir.
- Teknik resim ve STEP exportlari hazirlanir.

**Ciktilar**
- Guncel FreeCAD montaji
- Imalata uygun teknik resimler
- STEP exportlari
- Mekanik BOM

**Bagimlilik**
- Faz 2 onayi olmadan mekanik cizimler dondurulmamali.

## Faz 4: Elektrik Proje ve Panel Tasarimi

**Hedef:** Kablolama ve pano kurulumu hata yapmadan uygulanabilsin.

**Yapilacaklar**
- KiCad/Fritzing semalari gercek saha envanterine gore guncellenir.
- Ana guc, STO, EtherCAT, DI, DO, AI ve terminal planlari tamamlanir.
- Yeni lamine modulu icin ikinci R1-EC bus coupler baglantilari islenir.
- Servo, I/O, sensor ve isitici baglantilari terminal bazinda numaralandirilir.
- Pano yerlesimi, kablo kesitleri ve topraklama plani cikarilir.

**Ciktilar**
- Onayli sematik seti
- Terminal plani
- Kablo listesi
- Pano yerlesim plani

**Tamamlanma Kriteri**
- Elektrik montaj ekibi sadece dokumana bakarak saha kurulumunu yapabilir durumda olmali.

## Faz 5: Otomasyon ve Yazilim Gelistirme

**Hedef:** NC300, servo suruculer ve I/O sistemi kontrollu sekilde devreye alinabilsin.

**Yapilacaklar**
- EtherCAT topolojisi NC300 uzerinde olusturulur.
- Tüm eksenlerin temel parametreleri, encoder ayarlari ve limit mantiklari tanimlanir.
- PLC ana akisi; referans alma, interlock, alarm, manual/jog ve otomatik mod olarak ayrilir.
- Lamine kesim icin E-Cam ve senkron hareket yapisi kurulur.
- HMI ekranlari; durum, alarm, manuel kontrol, recipe ve servis sayfalari ile tamamlanir.
- AI destekli parametre hesabi yalnizca temel makine stabil olduktan sonra devreye alinacak sekilde ikincil katman olarak kurgulanir.

**Ciktilar**
- NC300 konfigrasyonu
- PLC yazilimi
- HMI ekranlari
- Alarm listesi
- Parametre yedekleme paketi

**Bagimlilik**
- Faz 4 adresleme yapisi sabitlenmeden PLC yazilimi dondurulmamali.

## Faz 6: Atolye Montaj ve Entegrasyon

**Hedef:** Tasarim verilerinin fiziksel sisteme kontrollu aktarimi.

**Yapilacaklar**
- Mekanik montaj ve eksen hizalamalari yapilir.
- Servo motorlar, kaplinler, raylar ve sensorler takilir.
- Pano montaji ve saha kablolamasi tamamlanir.
- EtherCAT, STO ve I/O baglantilari checklist ile tek tek dogrulanir.
- Enerji vermeden once sureklilik ve izolasyon kontrolleri yapilir.

**Ciktilar**
- Montaji tamamlanmis makina
- Kablolama checklistleri
- Devreye alma oncesi kontrol formu

## Faz 7: Devreye Alma ve Fonksiyon Testleri

**Hedef:** Hareket, guvenlik ve proses akisi kontrollu sekilde dogrulansin.

**Test Sirasi**
1. Enerji dagitimi ve emniyet zinciri kontrolu
2. STO testi
3. I/O tekil testleri
4. Servo enable ve yon kontrolu
5. Referans donusleri
6. Manuel hareket testleri
7. EtherCAT haberlesme stabilite testi
8. Ust kesim prosesi
9. Alt kesim ve V ekseni senkronizasyonu
10. Isitma, ayirma ve kirma sekanslari
11. Tam lamine kesim dongusu

**Ciktilar**
- SAT/FAT test listeleri
- Alarm ve hata kayitlari
- Parametre revizyon listesi

**Tamamlanma Kriteri**
- Tum emniyet fonksiyonlari dogrulanmis ve temel kesim cevrimi stabil calisiyor olmali.

## Faz 8: Performans ve Kabul

**Hedef:** Makinenin surekli calisma ve proses uygunlugu acisindan onaylanmasi.

**Yapilacaklar**
- Hassasiyet, tekrar edebilirlik ve hiz testleri yapilir.
- Duz cam ve lamine cam icin farkli recipe testleri uygulanir.
- 72 saat surekli calisma veya esdeger dayanim testi yapilir.
- Kritik yedek parametreler ve geri donus paketi olusturulur.
- Operatör ve bakim ekiplerine egitim verilir.

**Ciktilar**
- Kabul test raporu
- Son parametre yedegi
- Operator kullanim notlari
- Bakim kontrol listesi

---

## 3. Onerilen Is Paketleri

### A. Mekanik Paket
- Motor ve flans montajlari
- V ekseni tasarimi
- Sensor ve pneumatik aparatlari
- Ana montaj ve cakisma kontrolu

### B. Elektrik Paket
- Guc ve kontrol semalari
- EtherCAT ve I/O topolojisi
- STO ve guvenlik devresi
- Terminal ve kablo plani

### C. Yazilim Paket
- NC300 eksen konfigurasyonu
- PLC siralama ve interlock yapisi
- E-Cam ve lamine proses sekansi
- HMI ve alarm yonetimi

### D. Devreye Alma Paket
- I/O testleri
- Hareket testleri
- Guvenlik testleri
- Proses kabul testleri

---

## 4. Kritik Bagimliliklar

- Mekanik offset ve referans noktalar netlesmeden V ekseni senkronizasyonu dogru kurulamaz.
- I/O adresleri sabitlenmeden PLC ve HMI tarafinda tekrar is olusur.
- STO mimarisi pano imalatindan once dondurulmalidir.
- Ust ve alt kesim koordinat kalibrasyonu tamamlanmadan lamine deneme kesimlerine gecilmemelidir.
- AI tabanli optimizasyon, temel proses kararliligi saglandiktan sonra devreye alinmalidir.

---

## 5. Onerilen Haftalik Yurutme Sirasi

### Hafta 1
- Saha kesfi
- Mevcut durum dokumani
- I/O ve mekanik referanslarin toplanmasi

### Hafta 2
- Sistem mimarisi onayi
- Ekipman ve I/O dondurma
- Risk listesinin kapanmasi

### Hafta 3-4
- FreeCAD mekanik model tamamlama
- Elektrik semalari ve terminal planlari

### Hafta 5-6
- NC300, EtherCAT ve PLC temel yapisinin kurulmasi
- HMI ana ekranlari ve alarm altyapisi

### Hafta 7
- Atolye montaj
- Pano ve saha kablolama

### Hafta 8
- I/O, STO ve eksen testleri
- Referans ve jog fonksiyonlari

### Hafta 9
- Duz cam kesim testleri
- Lamine modulu sekans testleri

### Hafta 10
- Tam proses denemeleri
- Hassasiyet ve sureklilik testleri
- Kabul ve devir dokumantasyonu

---

## 6. Yonetimsel Takip Tablosu

Her hafta asagidaki basliklarla ilerleme takibi yapilmalidir:

- Acik teknik kararlar
- Geciken is kalemleri
- Tedarik riski olan ekipmanlar
- Dokumani tamamlanan kalemler
- Testte kalan arizalar
- Sonraki haftanin saha hedefleri

---

## 7. Oncelikli Ilk 5 Adim

1. Saha bazli mevcut I/O ve mekanik envanteri tamamla.
2. V ekseni ve lamine modulu kapsam onayini kesinlestir.
3. Elektrik adresleme yapisini sabitle.
4. FreeCAD ana montaj ile pano/ekipman yerlesimini dondur.
5. NC300 EtherCAT ve temel PLC iskeletini kur.

---

## 8. Basari Olcutleri

- Tum eksenler referans donusu ve manuel hareket testlerini hatasiz gecmeli.
- STO ve emniyet zinciri dogrulanmali.
- Duz cam kesim prosesi stabil hale gelmeli.
- Lamine kesimde ust-alt kesim cizgileri tolerans icinde ortusmeli.
- Kritik recipe parametreleri dokumante edilmeli.
- Devreye alma sonrasi tekrar is oranlari dusuk kalmali.

