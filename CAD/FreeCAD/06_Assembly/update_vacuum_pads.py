#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vakum Padleri Güncelleme Scripti
Kartezyen köprü üzerindeki vakum padlerini görünür yapar

FreeCAD Python Console'da çalıştırın:
exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly/update_vacuum_pads.py").read())
update_vacuum_pads()
"""

import FreeCAD as App
import Part

def update_vacuum_pads():
    """
    Mevcut GFB-60/30RE-S modelindeki vakum padlerini günceller
    """
    print("=" * 60)
    print("VAKUM PADLERİ GÜNCELLEME")
    print("=" * 60)
    
    doc = App.ActiveDocument
    if doc is None:
        print("❌ Aktif FreeCAD belgesi bulunamadı!")
        print("Lütfen GFB-60/30RE-S modelini açın.")
        return None
    
    print(f"\n✓ Aktif belge: {doc.Label}")
    
    # Y Carriage'ı bul
    y_carriage = doc.getObject("Y_Carriage")
    if y_carriage is None:
        print("⚠️  Y_Carriage bulunamadı - önce model oluşturulmalı")
        return None
    
    print("✓ Y_Carriage bulundu")
    
    # Vakum manifoldunu bul veya oluştur
    vacuum_manifold = doc.getObject("Portal_Vacuum_Manifold")
    if vacuum_manifold is None:
        print("  → Vakum manifoldu oluşturuluyor...")
        # Manifold oluştur
        manifold = Part.makeBox(
            360, 55, 95,
            App.Vector(
                y_carriage.Placement.Base.x + 20,
                y_carriage.Placement.Base.y - 120,
                y_carriage.Placement.Base.z + 15
            )
        )
        vacuum_manifold = doc.addObject("Part::Feature", "Portal_Vacuum_Manifold")
        vacuum_manifold.Shape = manifold
        vacuum_manifold.ViewObject.ShapeColor = (0.93, 0.93, 0.93)
    else:
        print("✓ Vakum manifoldu bulundu")
    
    # Vakum padlerini oluştur/güncelle (4 adet, 80mm aralıklı)
    pad_positions = [0, 80, 160, 240]  # mm aralıklar
    
    created_pads = []
    for idx, y_offset in enumerate(pad_positions, start=1):
        pad_name = f"Portal_Vacuum_Cup_{idx}"
        existing_pad = doc.getObject(pad_name)
        
        if existing_pad:
            print(f"  ✓ {pad_name} güncelleniyor...")
            # Pozisyonu güncelle
            existing_pad.Placement = App.Placement(
                App.Vector(
                    vacuum_manifold.Placement.Base.x + 45,
                    vacuum_manifold.Placement.Base.y + y_offset,
                    y_carriage.Placement.Base.z - 8
                ),
                App.Rotation(0, 0, 0)
            )
            created_pads.append(existing_pad)
        else:
            print(f"  → {pad_name} oluşturuluyor...")
            # Yeni pad oluştur
            pad = Part.makeCylinder(
                26,     # Radius (52mm çap)
                28,     # Height
                App.Vector(
                    vacuum_manifold.Placement.Base.x + 45,
                    vacuum_manifold.Placement.Base.y + y_offset,
                    y_carriage.Placement.Base.z - 8
                ),
                App.Vector(0, 0, 1)
            )
            pad_feature = doc.addObject("Part::Feature", pad_name)
            pad_feature.Shape = pad
            pad_feature.ViewObject.ShapeColor = (0.15, 0.15, 0.18)  # Koyu gri
            created_pads.append(pad_feature)
    
    # Belgeyi güncelle
    doc.recompute()
    
    print("\n" + "=" * 60)
    print("✓ TAMAMLANDI")
    print("=" * 60)
    print(f"\nOluşturulan/Güncellenen padler: {len(created_pads)}")
    for pad in created_pads:
        print(f"  - {pad.Label}: X={pad.Placement.Base.x:.1f}, "
              f"Y={pad.Placement.Base.y:.1f}, Z={pad.Placement.Base.z:.1f}")
    
    print("\n💡 İpucu: View → Fit All (V) ile tüm modeli görün")
    
    return created_pads


def verify_vacuum_system():
    """
    Vakum sisteminin görsel doğrulamasını yap
    """
    doc = App.ActiveDocument
    if doc is None:
        print("❌ Aktif belge yok")
        return
    
    print("\n" + "=" * 60)
    print("VAKUM SİSTEMİ DOĞRULAMA")
    print("=" * 60)
    
    # Tüm vakum bileşenlerini bul
    vacuum_objects = []
    for obj in doc.Objects:
        if "Vacuum" in obj.Name or "Vakum" in obj.Label:
            vacuum_objects.append(obj)
    
    if not vacuum_objects:
        print("\n⚠️  Vakum bileşeni bulunamadı!")
        print("update_vacuum_pads() fonksiyonunu çalıştırın.")
        return
    
    print(f"\nBulunan vakum bileşenleri: {len(vacuum_objects)}")
    for obj in vacuum_objects:
        visible = obj.ViewObject.Visibility if hasattr(obj, 'ViewObject') else 'N/A'
        print(f"  - {obj.Label}: Görünürlük={visible}")
    
    # Padleri kontrol et
    pad_count = sum(1 for obj in vacuum_objects if "Cup" in obj.Name or "Pad" in obj.Label)
    print(f"\nVakum padleri: {pad_count} adet")
    
    if pad_count >= 4:
        print("✅ Vakum sistemi doğru yapılandırılmış")
    else:
        print("⚠️  En az 4 vakum pad'i önerilir")


if __name__ == "__main__":
    # Ana fonksiyonu çalıştır
    pads = update_vacuum_pads()
    
    # Doğrulama
    if pads:
        verify_vacuum_system()
