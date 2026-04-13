# Operator Terminal Imalat Brief

**Proje:** LiSEC GFB-60/30RE  
**Tarih:** 12.04.2026  
**Amac:** Panocunun ayakli operator terminalini, Beckhoff benzeri sade endustriyel form ve LiSEC saha ergonomisine uygun sekilde imal etmesi

---

## Genel Form

Terminal, duvara asili bir kutu gibi degil; bagimsiz ayakli operator istasyonu gibi uretilmelidir.

Form 3 ana bolumden olusur:

1. Agir taban
2. Kablo gizleyen kolon
3. One hafif egimli terminal basligi

---

## Tasarim Dili

- Sade, temiz, endustriyel
- Ince cerceveli on yuz
- Sert koseli ama kaba durmayan geometri
- Kablo ve baglantilar disaridan minimum gorunmeli
- Makine yaninda sabit operator istasyonu hissi vermeli

Referans karakter:

- Beckhoff ayakli panel/panel PC ailesi
- LiSEC operator istasyonlarinin makineye yakin saha kullanimi

---

## Yerlesim Niyeti

- Terminal, koprunun home noktalarina yakin konumlanacak
- Operator home/referans hareketlerini dogrudan gorebilmeli
- HMI merkezi yaklasik `1100-1200 mm` seviyesinde olmali
- Ekran operatora hafif egimli bakmali

---

## Onerilen Mekanik Oranlar

### 1. Taban

- Yaklasik taban olcusu: `520 x 420 mm`
- Sac veya kutu konstruksiyon agir taban
- Devrilmeye direncli olmali
- Gerekirse taban icine agirlik plakasi eklenebilir

### 2. Kolon

- Yaklasik kolon kesiti: `150 x 110 mm`
- Kablo gecisi kolon icinden olmali
- Dis gorunum sade, on yuz mumkunse duz olmali
- Bakim icin arka veya alt erisim dusunulmeli

### 3. Terminal Basligi

- Yaklasik baslik olcusu: `420 x 340 x 220 mm`
- DOP-110CS icin on yuz cutout uygulanacak
- Cerceve kalinligi gereksiz buyutulmemeli
- Baslik kolon ustunde one cikan bir tasiyici ile desteklenmeli

---

## HMI ve On Yuz

- HMI: `Delta DOP-110CS`
- Cutout referansi: `DOP-110CS_Panel_Cutout.stp`
- On yuzde ekran etrafinda temiz ve simetrik bir bordur olmali
- HMI cevresi Beckhoff benzeri duz/on cam etkisi verecek sekilde sakin tutulmali
- `S0 E-STOP` operator paneli uzerinde olmali
- E-STOP, operatorun ekran ile birlikte ayni istasyondan ulasabilecegi noktada konumlanmali
- Oneri: on yuz alt-sag veya sag yan on bolge

---

## Malzeme ve Imalat Niyeti

- Govde: boyali sac celik veya paslanmaz secenekli dusunulebilir
- Tipik sac kalinligi: `2-5 mm` araligi
- Dis yuzeyler kolay temizlenebilir olmali
- Kose birlesimleri endustriyel ama duzgun bitisli olmali
- Gerekirse gizli civata / icten baglanti tercih edilmeli

---

## Kablo ve Baglanti

- 24VDC, 0V, PE ve Ethernet ana panodan gelecek
- Kablolar kolon icinden terminal basligina cikacak
- Kablo rakorlari ve servis erisimi alt/arka bolgede toplanmali
- Disaridan sarkik kablo gorunumu olmamali

---

## Panocu Icin Net Beklenti

Panocudan beklenen, mevcut kutu mantigini birebir kopyalamasi degil; asagidaki karakterde bir imalat yapmasidir:

- makineden bagimsiz ayakta duran
- operatora donuk
- sade ve premium gorunumlu
- saha kullanimina dayanikli
- HMI odakli kompakt operator istasyonu
- acil durdurma butonunu operator paneline entegre eden guvenli istasyon

---

## Paket Icindeki Ilgili Dosyalar

- `Operator_Terminal_Generator.py`
- `README_Operator_Terminal.md`
- `DOP-110CS_Panel_Cutout.stp`
- `Operator_Terminal_Enclosure.stp`
- `Operator_Terminal_Door.stp`
- `R1-EC_Mounting_Plate.stp`
