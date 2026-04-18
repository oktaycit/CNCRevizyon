# FreeCAD NC300 Clear Path Analizi

Tarih: 2026-04-18  
Model: `/Users/oktaycit/Projeler/CNCRevizyon/CAD/30RE-S Hibrit Sistem.FCStd`  
Kaynaklar:
- `FCStd` içindeki `Document.xml` ve spreadsheet kayıtları
- `/Users/oktaycit/Projeler/CNCRevizyon/Documentation/Reports/FreeCAD_Lamine_Sync_Simulation_2026-04-17.md`
- `/Users/oktaycit/Projeler/CNCRevizyon/Electrical/Panel_Replacement_Workflow.md`
- `/Users/oktaycit/Projeler/CNCRevizyon/Electrical/Panel_Manufacturer/02_TERMINAL_DIAGRAMS.md`

Not:
- Bu makinede FreeCAD runtime doğrudan açılamadığı için son kontrol `FCStd` arşiv içeriği ve mevcut MCP çıktıları üzerinden yapılmıştır.

## 1. Doğrulanan Model Noktaları

- `Variables` spreadsheet mevcut ve temel hücreler `A1..S1` saklanmış durumda.
- `Q1 = 18 mm`, `R1 = 5 mm`, `S1 = 2 mm` model içinde kayıtlıdır.
- `Lower_Cutter_Head` halen `V_Carriage` üzerinden sürülüyor, ancak `R1` alt kesici kinematiğinde kullanılmıyor.
- `Heater_Rod` ifadesi:
  - `.Placement.Base.x = 200 mm + Variables.B1`
  - `.Placement.Base.z = Table_Grid.Placement.Base.z + Table_Grid.Height - Variables.Q1 - 15 mm`
- `Lamine_IO` ve `Lamine_Phases` spreadsheet’leri model içinde mevcut.

## 2. Çakışmasız Hareket Yolu

### 2.1 Alt kesici clear path

Geçerli modelden okunan kanal referansı:
- `Lower_Cutter_Channel_Reference`: `Y = 1350..2250 mm`
- kanal genişliği: `900 mm`

Geçerli alt kafa gövdesi:
- `Lower_Cutter_Head`: `Y tabanı = 1450 mm`, `Width = 100 mm`

Buna göre sadece kanal içinde kalma şartı için teorik `Variables.D1` penceresi:
- minimum: `-100 mm`
- maksimum: `+700 mm`

Komisyoning için önerilen emniyetli pencere:
- `Variables.D1 = -80 .. +640 mm`

Önerilen clear-path kuralı:
1. Alt kafa gövdesi tamamen alt kanalda kalmalı.
2. Tabla içine sadece teker ve ince takım boynu girmeli.
3. Mazgal / geçiş boşluğu takım hattında lokal slot olarak açılmalı; gövde tabla alt yüzeyinin altında kalmalı.

Bu yüzden mekanik onay için gerekli revizyon:
- `Lower_Cutter_Head` gövdesi için ayrı "under-table body" zarfı korunmalı.
- `Lower_Cutting_Wheel` için tabla slotu veya dar geçiş boynu tanımlanmalı.
- `R1` doğrudan alt kesici çalışma geometrisine bağlanmalı; mevcut FCStd’de henüz bağlı değildir.

### 2.2 Isıtıcı clear path

Modelde ısıtıcı stroku `B1` ile X boyunca izleniyor. Nominal boşluk mantığı:
- `Q1 = 18 mm`
- rod formülündeki `-15 mm`, silindir yarıçapını temsil eder
- dolayısıyla cam alt yüzeyine nominal yüzey boşluğu `18 mm` olarak okunur

Önerilen clear-path kuralı:
1. `HEATER_DOWN` sadece `VACUUM_OK = 1` ve `EDGE_PROBE_OK = 1` sonrası aktif olmalı.
2. `HEATER_ENABLE` yalnız `HEATER_DOWN_OK = 1` iken verilmelidir.
3. `HEATER_UP_OK = 1` olmadan senkron kesim fazına geçilmemelidir.

## 3. Folyo Germe için X Offset Parametreleri

Model değişkenlerine aktarılan yeni hücreler:
- `T1`: yükleme köprüsü net X düzeltmesi
- `U1`: G31 kenar bulma sonrası güvenli geri kaçış, nominal `8 mm`
- `V1`: folyo germe geri çekme miktarı, nominal `3 mm`
- `W1`: germe sonrası gevşetme / settle payı, nominal `1 mm`

Önerilen NC hesabı:

```text
T1 := -(U1 + V1 - W1)
```

Nominal reçete ile:

```text
T1 := -(8 + 3 - 1) = -10 mm
```

Anlamı:
- köprü önce G31 ile kenarı bulur
- ardından `8 mm` emniyetli geri kaçış yapar
- ekstra `3 mm` geri çekerek folyo gerer
- son olarak `1 mm` bırakıp camı stabil tutar

Model tarafında:
- `Loading_Station_Carriage`
- `Loading_Suction_Beam`
- `Loading_Vacuum_Manifold`
- `Loading_Suction_Pad_*`

objeleri artık `Variables.T1` ile birlikte X düzeltmesi alacak şekilde güncellenmiştir.

## 4. Delta NC300 I/O Haritalama Önerisi

### 4.1 Mevcut temel limit / home girişleri

Sahadaki mevcut Leuze IS 218 eşleşmesi:
- `S10 / %IX0.2`: X home
- `S11 / %IX0.0`: X+ limit
- `S12 / %IX0.1`: X- limit
- `S20 / %IX0.5`: Y home
- `S21 / %IX0.3`: Y+ limit
- `S22 / %IX0.4`: Y- limit
- `S30 / %IX0.8`: Z home
- `S31 / %IX0.6`: Z+ limit
- `S40 / %IX0.11`: Alt home
- `S41 / %IX0.9`: Alt+ limit
- `S42 / %IX0.10`: Alt- limit
- `S51 / %IX0.15`: Vacuum OK

### 4.2 Lamine modül için önerilen DI

Önerilen ek DI bankası (`R1-EC0902D #4`, `%IX2.x`):
- `%IX2.0`: `EDGE_PROBE_OK`
- `%IX2.1`: `TENSION_OK`
- `%IX2.2`: `HEATER_DOWN_OK`
- `%IX2.3`: `HEATER_UP_OK`
- `%IX2.4`: `TEMP_READY`
- `%IX2.5`: `GLASS_DETECT`
- `%IX2.6`: `LOWER_HEAD_READY`
- `%IX2.7`: `LOWER_CUT_OK`

### 4.3 Lamine modül için önerilen DO

Önerilen ek DO bankası (`R1-EC0902O #4`, `%QX2.x`):
- `%QX2.0`: `LOADING_VACUUM_ENABLE`
- `%QX2.1`: `EDGE_PROBE_ENABLE`
- `%QX2.2`: `TENSION_RETRACT_ENABLE`
- `%QX2.3`: `HEATER_DOWN`
- `%QX2.4`: `HEATER_ENABLE`
- `%QX2.5`: `HEATER_ZONE_1`
- `%QX2.6`: `HEATER_ZONE_2`
- `%QX2.7`: `HEATER_SAFETY_ENABLE`
- `%QX2.8`: `LOWER_CUT_ENABLE`
- `%QX2.9`: `PRESSURE_ROLLER`
- `%QX2.10`: `SEPARATING_BLADE`
- `%QX2.11`: `BREAKING_BAR`

## 5. NC300 Faz Kuralı

Önerilen faz sırası:
1. `Yukleme`
2. `Kenar Probu`
3. `Folyo Germe`
4. `Isitici Inis`
5. `Isitma`
6. `Isitici Kalkis`
7. `Ust Kesim`
8. `Alt Kesici Hazirlik`
9. `Senkronize Kesim`

Kritik interlock:
- `VACUUM_OK` olmadan `EDGE_PROBE_ENABLE` verilmez.
- `EDGE_PROBE_OK` olmadan `TENSION_RETRACT_ENABLE` verilmez.
- `HEATER_UP_OK` olmadan `LOWER_CUT_ENABLE` verilmez.
- Leuze home / limit sinyalleri zamanlama simülasyonunda sanal DI olarak izlenmelidir.
