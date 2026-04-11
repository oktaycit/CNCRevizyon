#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blade Management Module
Cutting blade life tracking and spin control for glass cutting

Features:
- Blade life tracking (meters cut)
- Spin control (rotate blade for even wear)
- Blade change alerts
- Grinding allowance (taşlama payı)
- Blade history
"""

import math
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from enum import Enum


class BladeType(Enum):
    """Blade types for different glass"""
    STANDARD = "standard"  # Normal cam
    LAMINATED = "laminated"  # Lamine cam
    TEMPERED = "tempered"  # Temperli cam
    DIAMOND = "diamond"  # Elmas uç (sert cam)
    CARBIDE = "carbide"  # Karbür uç


class BladeStatus(Enum):
    """Blade status"""
    NEW = "new"
    ACTIVE = "active"
    WARNING = "warning"  # Yakında değişmeli
    EXPIRED = "expired"  # Değişmeli
    SPIN_REQUIRED = "spin_required"  # Döndürülmeli


@dataclass
class Blade:
    """Cutting blade"""
    blade_id: str
    blade_type: BladeType
    installed_date: datetime
    total_life: float  # meters (max cutting length)
    used_life: float = 0.0  # meters cut
    spin_count: int = 0  # Number of spins
    last_spin_date: Optional[datetime] = None
    spin_interval: float = 1000.0  # meters between spins
    status: BladeStatus = BladeStatus.NEW
    
    # Grinding allowance (taşlama payı)
    grinding_allowance_x: float = 0.0  # mm (each side)
    grinding_allowance_y: float = 0.0  # mm (each side)
    
    @property
    def remaining_life(self) -> float:
        """Remaining blade life in meters"""
        return max(0, self.total_life - self.used_life)
    
    @property
    def life_percentage(self) -> float:
        """Remaining life percentage"""
        return (self.remaining_life / self.total_life) * 100
    
    @property
    def needs_spin(self) -> bool:
        """Check if blade needs spinning"""
        if self.last_spin_date is None:
            return self.used_life >= self.spin_interval
        
        return (self.used_life - (self.spin_count * self.spin_interval)) >= self.spin_interval
    
    def update_status(self):
        """Update blade status based on life"""
        if self.life_percentage <= 0:
            self.status = BladeStatus.EXPIRED
        elif self.life_percentage <= 20:
            self.status = BladeStatus.WARNING
        elif self.needs_spin:
            self.status = BladeStatus.SPIN_REQUIRED
        else:
            self.status = BladeStatus.ACTIVE
    
    def add_cut_length(self, length: float):
        """Add cut length to used life"""
        self.used_life += length
        self.update_status()
    
    def spin_blade(self):
        """Spin the blade (rotate to new position)"""
        self.spin_count += 1
        self.last_spin_date = datetime.now()
        self.update_status()
    
    def reset(self):
        """Reset blade to new condition"""
        self.used_life = 0.0
        self.spin_count = 0
        self.last_spin_date = None
        self.status = BladeStatus.NEW
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "blade_id": self.blade_id,
            "blade_type": self.blade_type.value,
            "installed_date": self.installed_date.isoformat(),
            "total_life": self.total_life,
            "used_life": self.used_life,
            "remaining_life": self.remaining_life,
            "life_percentage": self.life_percentage,
            "spin_count": self.spin_count,
            "last_spin_date": self.last_spin_date.isoformat() if self.last_spin_date else None,
            "spin_interval": self.spin_interval,
            "status": self.status.value,
            "needs_spin": self.needs_spin,
            "grinding_allowance_x": self.grinding_allowance_x,
            "grinding_allowance_y": self.grinding_allowance_y
        }


@dataclass
class GrindingAllowance:
    """Grinding allowance for edge processing"""
    allowance_type: str  # none, grinding, polishing, bevelling
    x_allowance: float  # mm (added to width, each side)
    y_allowance: float  # mm (added to height, each side)
    description: str = ""
    
    @property
    def total_x_addition(self) -> float:
        """Total addition to X dimension (both sides)"""
        return self.x_allowance * 2
    
    @property
    def total_y_addition(self) -> float:
        """Total addition to Y dimension (both sides)"""
        return self.y_allowance * 2


class BladeManager:
    """Manage cutting blades"""
    
    # Standard grinding allowances
    GRINDING_ALLOWANCES = {
        "none": GrindingAllowance("none", 0, 0, "İşlem yok"),
        "grinding": GrindingAllowance("grinding", 2, 2, "Kaba taşlama"),
        "fine_grinding": GrindingAllowance("fine_grinding", 1, 1, "İnce taşlama"),
        "polishing": GrindingAllowance("polishing", 1.5, 1.5, "Parlatma"),
        "bevelling": GrindingAllowance("bevelling", 3, 3, "Pah kırma"),
        "edge_sealing": GrindingAllowance("edge_sealing", 0.5, 0.5, "Kenar contası"),
    }
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path) if data_path else Path(__file__).parent.parent / 'data'
        self.blades: Dict[str, Blade] = {}
        self.active_blade_id: Optional[str] = None
        self.cut_history: List[Dict] = []
        
        # Load existing data
        self.load()
    
    def install_blade(self,
                      blade_id: str,
                      blade_type: BladeType,
                      total_life: float = 5000.0,  # 5000m default
                      spin_interval: float = 1000.0) -> Blade:
        """Install new blade"""
        blade = Blade(
            blade_id=blade_id,
            blade_type=blade_type,
            installed_date=datetime.now(),
            total_life=total_life,
            spin_interval=spin_interval
        )
        
        self.blades[blade_id] = blade
        self.active_blade_id = blade_id
        self.save()
        
        return blade
    
    def get_blade(self, blade_id: str) -> Optional[Blade]:
        """Get blade by ID"""
        return self.blades.get(blade_id)
    
    def get_active_blade(self) -> Optional[Blade]:
        """Get active blade"""
        if self.active_blade_id:
            return self.blades.get(self.active_blade_id)
        return None
    
    def set_active_blade(self, blade_id: str) -> bool:
        """Set active blade"""
        if blade_id in self.blades:
            self.active_blade_id = blade_id
            self.save()
            return True
        return False
    
    def record_cut(self, length: float, order_id: str = ""):
        """Record a cut operation"""
        blade = self.get_active_blade()
        if blade:
            blade.add_cut_length(length)
            
            # Record in history
            self.cut_history.append({
                "timestamp": datetime.now().isoformat(),
                "blade_id": blade.blade_id,
                "length": length,
                "order_id": order_id,
                "total_used": blade.used_life
            })
            
            # Keep history to last 1000 entries
            if len(self.cut_history) > 1000:
                self.cut_history = self.cut_history[-1000:]
            
            self.save()
    
    def spin_active_blade(self) -> bool:
        """Spin the active blade"""
        blade = self.get_active_blade()
        if blade and blade.needs_spin:
            blade.spin_blade()
            self.save()
            return True
        return False
    
    def replace_blade(self, new_blade_id: str, blade_type: BladeType) -> Blade:
        """Replace current blade with new one"""
        # Archive old blade
        old_blade = self.get_active_blade()
        if old_blade:
            old_blade.status = BladeStatus.EXPIRED
        
        # Install new blade
        return self.install_blade(new_blade_id, blade_type)
    
    def get_blade_alerts(self) -> List[Dict]:
        """Get blade alerts"""
        alerts = []
        
        for blade in self.blades.values():
            if blade.status == BladeStatus.EXPIRED:
                alerts.append({
                    "type": "error",
                    "message": f"Bıçak {blade.blade_id} ömrünü tamamladı! Değiştirin.",
                    "blade_id": blade.blade_id,
                    "life_remaining": 0
                })
            elif blade.status == BladeStatus.WARNING:
                alerts.append({
                    "type": "warning",
                    "message": f"Bıçak {blade.blade_id} ömrü % {blade.life_percentage:.1f}. Yakında değiştirin.",
                    "blade_id": blade.blade_id,
                    "life_remaining": blade.life_percentage
                })
            elif blade.status == BladeStatus.SPIN_REQUIRED:
                alerts.append({
                    "type": "info",
                    "message": f"Bıçak {blade.blade_id} döndürülmeli. Son {blade.spin_interval:.0f}m kesim yapıldı.",
                    "blade_id": blade.blade_id,
                    "action": "spin"
                })
        
        return alerts
    
    def calculate_with_grinding(self,
                                width: float,
                                height: float,
                                allowance_type: str = "none") -> Dict:
        """
        Calculate dimensions with grinding allowance
        
        Args:
            width: Original width (mm)
            height: Original height (mm)
            allowance_type: Type of grinding
        
        Returns:
            Dictionary with adjusted dimensions
        """
        allowance = self.GRINDING_ALLOWANCES.get(allowance_type, self.GRINDING_ALLOWANCES["none"])
        
        return {
            "original_width": width,
            "original_height": height,
            "cutting_width": width + allowance.total_x_addition,
            "cutting_height": height + allowance.total_y_addition,
            "allowance_type": allowance_type,
            "x_allowance_each_side": allowance.x_allowance,
            "y_allowance_each_side": allowance.y_allowance,
            "total_x_addition": allowance.total_x_addition,
            "total_y_addition": allowance.total_y_addition
        }
    
    def save(self):
        """Save blade data to file"""
        data = {
            "blades": {bid: b.to_dict() for bid, b in self.blades.items()},
            "active_blade_id": self.active_blade_id,
            "cut_history": self.cut_history[-100:]  # Last 100 cuts
        }
        
        self.data_path.mkdir(parents=True, exist_ok=True)
        with open(self.data_path / 'blades.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self):
        """Load blade data from file"""
        blade_file = self.data_path / 'blades.json'
        
        if blade_file.exists():
            with open(blade_file, 'r') as f:
                data = json.load(f)
            
            self.active_blade_id = data.get('active_blade_id')
            self.cut_history = data.get('cut_history', [])
            
            for bid, bdata in data.get('blades', {}).items():
                blade = Blade(
                    blade_id=bdata['blade_id'],
                    blade_type=BladeType(bdata['blade_type']),
                    installed_date=datetime.fromisoformat(bdata['installed_date']),
                    total_life=bdata['total_life'],
                    used_life=bdata.get('used_life', 0),
                    spin_count=bdata.get('spin_count', 0),
                    spin_interval=bdata.get('spin_interval', 1000)
                )
                
                if bdata.get('last_spin_date'):
                    blade.last_spin_date = datetime.fromisoformat(bdata['last_spin_date'])
                
                blade.grinding_allowance_x = bdata.get('grinding_allowance_x', 0)
                blade.grinding_allowance_y = bdata.get('grinding_allowance_y', 0)
                
                blade.update_status()
                self.blades[bid] = blade
    
    def get_statistics(self) -> Dict:
        """Get blade statistics"""
        total_blades = len(self.blades)
        active_blades = sum(1 for b in self.blades.values() if b.status == BladeStatus.ACTIVE)
        expired_blades = sum(1 for b in self.blades.values() if b.status == BladeStatus.EXPIRED)
        total_cuts = len(self.cut_history)
        total_length = sum(cut['length'] for cut in self.cut_history)
        
        return {
            "total_blades": total_blades,
            "active_blades": active_blades,
            "expired_blades": expired_blades,
            "total_cuts": total_cuts,
            "total_cut_length": total_length,
            "average_cut_length": total_length / total_cuts if total_cuts > 0 else 0
        }


def demo():
    """Demo usage"""
    print("=" * 60)
    print("Blade Management Demo")
    print("=" * 60)
    
    # Create manager
    manager = BladeManager()
    
    # Install blade
    print("\n🔧 Installing new blade...")
    blade = manager.install_blade(
        blade_id="BLADE-001",
        blade_type=BladeType.STANDARD,
        total_life=5000.0,
        spin_interval=1000.0
    )
    
    print(f"Blade ID: {blade.blade_id}")
    print(f"Type: {blade.blade_type.value}")
    print(f"Life: {blade.total_life}m")
    print(f"Status: {blade.status.value}")
    
    # Record some cuts
    print("\n✂️ Recording cuts...")
    for i in range(10):
        length = 50 + i * 10  # 50m, 60m, 70m...
        manager.record_cut(length, f"ORD-{i+1:03d}")
        print(f"  Cut {i+1}: {length}m (Total: {blade.used_life:.1f}m)")
    
    # Check status
    print(f"\n📊 Blade Status:")
    print(f"  Used: {blade.used_life:.1f}m / {blade.total_life}m")
    print(f"  Remaining: {blade.remaining_life:.1f}m")
    print(f"  Life: {blade.life_percentage:.1f}%")
    print(f"  Needs spin: {blade.needs_spin}")
    
    # Grinding allowance
    print("\n🔧 Grinding Allowance Test:")
    for allowance_type in ["none", "grinding", "fine_grinding", "polishing"]:
        result = manager.calculate_with_grinding(500, 400, allowance_type)
        print(f"  {allowance_type}:")
        print(f"    Original: {result['original_width']}x{result['original_height']}mm")
        print(f"    Cutting:  {result['cutting_width']}x{result['cutting_height']}mm")
        print(f"    Added:    +{result['total_x_addition']}mm (X) +{result['total_y_addition']}mm (Y)")
    
    # Alerts
    print("\n🔔 Alerts:")
    alerts = manager.get_blade_alerts()
    if alerts:
        for alert in alerts:
            print(f"  [{alert['type']}] {alert['message']}")
    else:
        print("  No alerts")
    
    # Statistics
    print("\n📈 Statistics:")
    stats = manager.get_statistics()
    print(f"  Total blades: {stats['total_blades']}")
    print(f"  Active blades: {stats['active_blades']}")
    print(f"  Total cuts: {stats['total_cuts']}")
    print(f"  Total length: {stats['total_cut_length']:.1f}m")


if __name__ == "__main__":
    demo()