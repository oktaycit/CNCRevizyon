# FreeCAD Şase (Frame) Modeli
# CNC Revizyon Projesi - GFB-60/30RE
# 6000 x 3000 mm Çalışma Alanı

import FreeCAD as App
import Part
import math
import os

# Base dizinini ayarla
try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/02_Frame"

EXPORT_DIR = os.path.join(BASE_DIR, "..", "07_Exports", "STEP", "Frame")
os.makedirs(EXPORT_DIR, exist_ok=True)

# Şase Parametreleri
FRAME_LENGTH = 6000  # X ekseni uzunluğu
FRAME_WIDTH = 3000   # Y ekseni genişliği
PROFILE_SIZE = 80    # Profil boyutu (80x80 mm)
PROFILE_THICKNESS = 4  # Profil et kalınlığı (mm)
FRAME_HEIGHT = 800   # Yerden yükseklik

def create_cylinder(radius, height, position=(0, 0, 0), direction=(0, 0, 1)):
    """Silindir oluştur"""
    return Part.makeCylinder(radius, height, 
                              App.Vector(position), 
                              App.Vector(direction))

def create_box(width, height, depth, position=(0, 0, 0)):
    """Kutu oluştur"""
    return Part.makeBox(width, height, depth, App.Vector(position))

def create_hollow_profile(size, thickness, length, position=(0, 0, 0)):
    """
    İçi boş kare profil oluştur
    
    Args:
        size: Profil dış boyutu (mm)
        thickness: Et kalınlığı (mm)
        length: Profil uzunluğu (mm)
        position: Pozisyon vektörü
    """
    # Dış kutu
    outer = create_box(size, size, length, 
                       (-size/2, -size/2, 0))
    
    # İç boşluk
    inner_size = size - 2 * thickness
    inner = create_box(inner_size, inner_size, length + 2,
                       (-inner_size/2, -inner_size/2, -1))
    
    # Boolean cut ile içi boş profil
    hollow = outer.cut(inner)
    
    # Pozisyonu ayarla
    moved = hollow.copy()
    moved.translate(App.Vector(position))
    
    return moved

def create_main_frame_profiles(doc, name="MainFrame_Profiles"):
    """
    Ana şase profillerini oluştur
    
    4 adet uzun profil (X ekseni - 6000 mm)
    4 adet kısa profil (Y ekseni - 3000 mm)
    """
    profiles = []
    
    # Uzun profiller (X ekseni) - 2 ön, 2 arka
    front_outer = create_hollow_profile(PROFILE_SIZE, PROFILE_THICKNESS, 
                                         FRAME_LENGTH, (0, 0, 0))
    front_inner = create_hollow_profile(PROFILE_SIZE, PROFILE_THICKNESS, 
                                         FRAME_LENGTH, (0, FRAME_WIDTH - PROFILE_SIZE, 0))
    rear_outer = create_hollow_profile(PROFILE_SIZE, PROFILE_THICKNESS, 
                                        FRAME_LENGTH, (0, FRAME_WIDTH, 0))
    rear_inner = create_hollow_profile(PROFILE_SIZE, PROFILE_THICKNESS, 
                                        FRAME_LENGTH, (0, FRAME_WIDTH - PROFILE_SIZE + PROFILE_THICKNESS, 0))
    
    profiles.extend([front_outer, front_inner, rear_inner, rear_outer])
    
    # Kısa profiller (Y ekseni) - 2 sol, 2 sağ
    left_outer = create_hollow_profile(PROFILE_SIZE, PROFILE_THICKNESS, 
                                        FRAME_WIDTH, (0, 0, 0))
    left_outer.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 90)
    left_outer.translate(App.Vector(0, 0, 0))
    
    left_inner = create_hollow_profile(PROFILE_SIZE, PROFILE_THICKNESS, 
                                        FRAME_WIDTH, (PROFILE_SIZE, 0, 0))
    left_inner.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 90)
    
    right_outer = create_hollow_profile(PROFILE_SIZE, PROFILE_THICKNESS, 
                                         FRAME_WIDTH, (0, 0, 0))
    right_outer.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 90)
    right_outer.translate(App.Vector(FRAME_LENGTH - PROFILE_SIZE, 0, 0))
    
    right_inner = create_hollow_profile(PROFILE_SIZE, PROFILE_THICKNESS, 
                                         FRAME_WIDTH, (PROFILE_SIZE, 0, 0))
    right_inner.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 90)
    right_inner.translate(App.Vector(FRAME_LENGTH - 2*PROFILE_SIZE, 0, 0))
    
    profiles.extend([left_outer, left_inner, right_inner, right_outer])
    
    # Tüm profilleri birleştir
    combined = profiles[0]
    for p in profiles[1:]:
        combined = combined.fuse(p)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = combined
    
    return shape

def create_support_leg(doc, name="SupportLeg", height=FRAME_HEIGHT, position=(0, 0, 0)):
    """
    Destek ayağı oluştur
    
    Ayarlanabilir ayak ile
    """
    leg_size = 100  # 100x100 mm ayak
    leg_thickness = 5
    
    # Ana ayak profili
    leg = create_hollow_profile(leg_size, leg_thickness, height, position)
    
    # Ayarlanabilir ayak tabanı
    base_plate = create_box(120, 20, 120, 
                            (position[0] - 60, position[1] - 10, position[2]))
    leg = leg.fuse(base_plate)
    
    # Dişli mil için delik
    thread_hole = create_cylinder(10, height + 5, 
                                  (position[0], position[1], position[2] - 2))
    leg = leg.cut(thread_hole)
    
    return leg

def create_corner_bracket(doc, name="CornerBracket", position=(0, 0, 0)):
    """
    Köşe takviye braketi oluştur
    
    8 mm sac kalınlığı
    M8 cıvata delikleri
    """
    bracket_size = 150  # 150x150 mm
    bracket_thickness = 8
    
    # L şeklinde braket
    vertical = create_box(bracket_thickness, bracket_size, bracket_size,
                          (0, 0, 0))
    horizontal = create_box(bracket_size, bracket_thickness, bracket_size,
                            (0, 0, 0))
    
    bracket = vertical.fuse(horizontal)
    
    # Cıvata delikleri (her iki yüzeyde)
    hole_radius = 4.5  # M8 için Ø9
    hole_positions = [
        (25, 25, 0),
        (125, 25, 0),
        (25, 125, 0),
        (125, 125, 0),
        (0, 25, 25),
        (0, 25, 125),
        (0, 125, 25),
        (0, 125, 125)
    ]
    
    for pos in hole_positions:
        # Pozisyonu ayarla
        actual_pos = (position[0] + pos[0], position[1] + pos[1], position[2] + pos[2])
        hole = create_cylinder(hole_radius, bracket_thickness + 2, actual_pos)
        bracket = bracket.cut(hole)
    
    return bracket

def create_frame_assembly(doc, name="Frame_Assembly"):
    """
    Tam şase montajı - Basitleştirilmiş versiyon
    Sadece ana profilleri döndürür (fuse hatası önlemek için)
    """
    # Ana profiller
    main_profiles = create_main_frame_profiles(doc, "Main_Profiles")
    
    return main_profiles

def create_portal_frame(doc, name="PortalFrame", width=2500, height=600):
    """
    X ekseni portal köprüsü
    
    Hareketli köprü yapısı
    """
    portal_profile = 120  # 120x120 mm profil
    portal_thickness = 6
    
    # İki dikey destek
    left_leg = create_hollow_profile(portal_profile, portal_thickness, height, (0, 0, 0))
    right_leg = create_hollow_profile(portal_profile, portal_thickness, height, 
                                      (width - portal_profile, 0, 0))
    
    # Üst köprü
    top_beam = create_hollow_profile(portal_profile, portal_thickness, width, (0, 0, 0))
    top_beam.rotate(App.Vector(0, 0, 0), App.Vector(1, 0, 0), 90)
    top_beam.translate(App.Vector(0, height - portal_profile, 0))
    
    # Birleştir
    portal = left_leg.fuse(right_leg)
    portal = portal.fuse(top_beam)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = portal
    
    return shape

def export_to_step(doc, obj, filename):
    """STEP dosyası olarak export et"""
    filepath = os.path.join(EXPORT_DIR, filename)
    Part.export([obj], filepath)
    print(f"  → {filepath} oluşturuldu")
    return filepath

def create_all_frame_parts():
    """Tüm şase parçalarını oluştur"""
    print("=" * 50)
    print("Şase (Frame) Generator - GFB-60/30RE")
    print("=" * 50)
    print(f"Şase Boyutları: {FRAME_LENGTH} x {FRAME_WIDTH} x {FRAME_HEIGHT} mm")
    print(f"Export dizini: {EXPORT_DIR}")
    print()
    
    # Ana şase
    print("Ana şase profilleri oluşturuluyor...")
    doc_frame = App.newDocument("MainFrame")
    frame = create_main_frame_profiles(doc_frame, "Main_Profiles")
    doc_frame.recompute()
    export_to_step(doc_frame, frame, "MainFrame_Profiles.stp")
    
    # Destek ayakları
    print("Destek ayakları oluşturuluyor...")
    doc_legs = App.newDocument("SupportLegs")
    legs = []
    for i, pos in enumerate([(0,0,0), (FRAME_LENGTH,0,0), (0,FRAME_WIDTH,0), (FRAME_LENGTH,FRAME_WIDTH,0)]):
        leg = create_support_leg(doc_legs, f"Leg_{i+1}", FRAME_HEIGHT, pos)
        legs.append(leg)
    doc_legs.recompute()
    export_to_step(doc_legs, legs[0], "SupportLeg.stp")
    
    # Köşe takviyeleri
    print("Köşe takviyeleri oluşturuluyor...")
    doc_brackets = App.newDocument("CornerBrackets")
    bracket = create_corner_bracket(doc_brackets, "Corner_Bracket", (0, 0, 0))
    doc_brackets.recompute()
    export_to_step(doc_brackets, bracket, "CornerBracket.stp")
    
    # Portal köprüsü
    print("Portal köprüsü oluşturuluyor...")
    doc_portal = App.newDocument("PortalFrame")
    portal = create_portal_frame(doc_portal, "Portal", FRAME_WIDTH - 200, 500)
    doc_portal.recompute()
    export_to_step(doc_portal, portal, "PortalFrame.stp")
    
    # Tam montaj
    print("Tam şase montajı oluşturuluyor...")
    doc_assembly = App.newDocument("Frame_Assembly")
    assembly = create_frame_assembly(doc_assembly, "Full_Frame")
    doc_assembly.recompute()
    export_to_step(doc_assembly, assembly, "Frame_Assembly.stp")
    
    print()
    print("=" * 50)
    print("Tüm şase parçaları oluşturuldu!")
    print("=" * 50)
    
    return doc_frame

if __name__ == "__main__":
    create_all_frame_parts()