# GFB60-30RE-S Devreye Alma Checklist

**Proje:** LiSEC GFB-60/30RE CNC Revizyon  
**Tarih:** 2026-04-09  
**Amac:** Ilk enerji verme, kontrol ve fonksiyon test sirasini standardize etmek

---

## 1. Enerji Vermeden Once

- [ ] Mekanik montaj tamamlandi.
- [ ] Tum pano kapaklari ve klemens kapaklari takili.
- [ ] Tum PE baglantilari sikildi.
- [ ] Servo, motor ve sensor kablolari etiketlendi.
- [ ] Guc ve sinyal kablolari ayrik guzergahlarda kontrol edildi.
- [ ] Ferrule ve klemens sikiliklari kontrol edildi.
- [ ] Faz sirasi ve ana giris gerilimi olculdu.
- [ ] 24VDC cikis hatti kisa devreye karsi kontrol edildi.

---

## 2. Pasif Elektrik Kontrolleri

- [ ] PE bara ile govde arasi sureklilik OK.
- [ ] PE ile surucu FG arasi sureklilik OK.
- [ ] 24V ile 0V arasinda kisa devre yok.
- [ ] STO hatlari guc hatlarindan ayrik cekildi.
- [ ] EtherCAT kablolarinin sirasi fiziksel olarak dogrulandi.
- [ ] Z ekseni fren kablosu polaritesi kontrol edildi.
- [ ] Sensor beslemeleri `+24V / 0V / OUT` olarak dogrulandi.

---

## 3. 24VDC Enerjilendirme

- [ ] Sadece kontrol beslemesi acildi.
- [ ] PS1 cikisi `24VDC +/-10%` olarak olculdu.
- [ ] NC300 besleme LED'leri normal.
- [ ] DOP-110CS aciliyor.
- [ ] R1-EC coupler power LED normal.
- [ ] Safety relay K10 besleme aliyor.
- [ ] Beklenmeyen isinma, koku veya sigorta atmasi yok.

---

## 4. Safety Testleri

- [ ] E-STOP serbestken K10 resetlenebiliyor.
- [ ] E-STOP basildiginda safety cikislari dusuyor.
- [ ] Door switch acildiginda safety cikislari dusuyor.
- [ ] Manual reset olmadan sistem tekrar enable olmuyor.
- [ ] STO cikislari tum eksenlere ulasiyor.
- [ ] STO aktifken servo torque kesiliyor.
- [ ] Safety geri bildirimleri NC300/R1-EC tarafinda goruluyor.

---

## 5. EtherCAT Baslangic

- [ ] NC300 acildi.
- [ ] EtherCAT agi tarandi.
- [ ] Slave 1: X servo gorundu.
- [ ] Slave 2: Y servo gorundu.
- [ ] Slave 3: Alt servo gorundu.
- [ ] Slave 4: Z servo gorundu.
- [ ] Slave 5: CNC servo gorundu.
- [ ] Slave 6: R1-EC gorundu.
- [ ] Tum slave'ler `OP` durumuna gecti.

---

## 6. I/O Testleri

- [ ] X+ limit `%IX0.0` dogru okuyor.
- [ ] X- limit `%IX0.1` dogru okuyor.
- [ ] X home `%IX0.2` dogru okuyor.
- [ ] Y+ limit `%IX0.3` dogru okuyor.
- [ ] Y- limit `%IX0.4` dogru okuyor.
- [ ] Y home `%IX0.5` dogru okuyor.
- [ ] Z+ limit `%IX0.6` dogru okuyor.
- [ ] Z- limit `%IX0.7` dogru okuyor.
- [ ] Z home `%IX0.8` dogru okuyor.
- [ ] Alt+ limit `%IX0.9` dogru okuyor.
- [ ] Alt- limit `%IX0.10` dogru okuyor.
- [ ] Alt home `%IX0.11` dogru okuyor.
- [ ] E-STOP kanallari `%IX0.12` ve `%IX0.13` dogru okuyor.
- [ ] Door input `%IX0.14` dogru okuyor.
- [ ] Vacuum feedback `%IX0.15` dogru okuyor.

---

## 7. Servo Testleri

- [ ] Servo enable mantigi dogrulandi.
- [ ] X ekseni jog test OK.
- [ ] Y ekseni jog test OK.
- [ ] Alt ekseni jog test OK.
- [ ] Z ekseni jog test OK.
- [ ] CNC/Rodaj ekseni jog test OK.
- [ ] Z ekseni fren acma-kapama mantigi dogru.
- [ ] Motor yonleri referansla uyumlu.
- [ ] Alarm cikislari ve reset mantigi test edildi.

---

## 8. Homing ve Fonksiyon Testleri

- [ ] X homing tamam.
- [ ] Y homing tamam.
- [ ] Z homing tamam.
- [ ] Alt homing tamam.
- [ ] Overtravel senaryolari dogru durduruyor.
- [ ] Vakum pompasi komutu dogru calisiyor.
- [ ] Uyari lambasi ve buzzer cikislari dogru.
- [ ] Konveyor ileri/geri mantigi dogru.

---

## 9. Final Kabul Notlari

- [ ] Tum test sonuclari kayit altina alindi.
- [ ] Degisen kablo/terminal numaralari dokumana islendi.
- [ ] Final wiring seti saha ile uyumlu hale getirildi.
- [ ] Yedek IO ve bos terminal alanlari not edildi.
- [ ] Operasyon ekibine handover yapildi.

