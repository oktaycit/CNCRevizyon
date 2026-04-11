#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Processing Module
Multi-sheet optimization and queue management for glass cutting

Features:
- Multi-sheet nesting
- Remnant management
- Order prioritization
- Cutting queue
- Batch optimization
- Sheet merging
"""

import math
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from enum import Enum
import json


class SheetStatus(Enum):
    """Sheet status"""
    AVAILABLE = "available"
    IN_USE = "in_use"
    PARTIAL = "partial"  # Partially used
    REMNANT = "remnant"  # Leftover piece
    WASTE = "waste"


class OrderPriority(Enum):
    """Order priority levels"""
    URGENT = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class GlassSheet:
    """Glass sheet representation"""
    sheet_id: str
    width: float
    height: float
    thickness: float
    glass_type: str
    status: SheetStatus = SheetStatus.AVAILABLE
    supplier: str = ""
    batch_number: str = ""
    cost: float = 0.0
    purchased_date: Optional[datetime] = None
    
    # Usage tracking
    used_area: float = 0.0
    parts: List[Dict] = field(default_factory=list)
    
    @property
    def total_area(self) -> float:
        return self.width * self.height
    
    @property
    def utilization(self) -> float:
        return self.used_area / self.total_area if self.total_area > 0 else 0
    
    @property
    def remaining_area(self) -> float:
        return self.total_area - self.used_area
    
    def to_dict(self) -> Dict:
        return {
            "sheet_id": self.sheet_id,
            "width": self.width,
            "height": self.height,
            "thickness": self.thickness,
            "glass_type": self.glass_type,
            "status": self.status.value,
            "utilization": self.utilization,
            "remaining_area": self.remaining_area,
            "parts_count": len(self.parts)
        }


@dataclass
class CuttingOrder:
    """Cutting order"""
    order_id: str
    width: float
    height: float
    quantity: int
    thickness: float
    glass_type: str
    priority: OrderPriority = OrderPriority.NORMAL
    customer: str = ""
    due_date: Optional[datetime] = None
    rotate_allowed: bool = True
    grinding_allowance: str = "none"
    
    # Processing status
    completed_quantity: int = 0
    assigned_sheet: Optional[str] = None
    
    @property
    def remaining_quantity(self) -> int:
        return self.quantity - self.completed_quantity
    
    @property
    def is_complete(self) -> bool:
        return self.completed_quantity >= self.quantity
    
    def to_dict(self) -> Dict:
        return {
            "order_id": self.order_id,
            "width": self.width,
            "height": self.height,
            "quantity": self.quantity,
            "completed_quantity": self.completed_quantity,
            "remaining_quantity": self.remaining_quantity,
            "glass_type": self.glass_type,
            "priority": self.priority.value,
            "is_complete": self.is_complete
        }


@dataclass
class CuttingJob:
    """Cutting job in queue"""
    job_id: str
    sheet: GlassSheet
    orders: List[CuttingOrder]
    nesting_result: Dict
    gcode_file: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_time: float = 0.0  # minutes
    actual_time: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            "job_id": self.job_id,
            "sheet_id": self.sheet.sheet_id,
            "orders": [o.order_id for o in self.orders],
            "status": self.status,
            "estimated_time": self.estimated_time,
            "actual_time": self.actual_time,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class BatchOptimizer:
    """Optimize cutting across multiple sheets"""
    
    def __init__(self):
        self.sheets: List[GlassSheet] = []
        self.orders: List[CuttingOrder] = []
        self.jobs: List[CuttingJob] = []
        self.remnants: List[GlassSheet] = []
    
    def add_sheet(self, sheet: GlassSheet):
        """Add sheet to available pool"""
        self.sheets.append(sheet)
    
    def add_order(self, order: CuttingOrder):
        """Add order to queue"""
        self.orders.append(order)
    
    def optimize_batch(self, strategy: str = "efficiency") -> List[CuttingJob]:
        """
        Optimize cutting across multiple sheets
        
        Args:
            strategy: "efficiency" (max utilization) or "speed" (min sheets)
        
        Returns:
            List of cutting jobs
        """
        jobs = []
        
        # Sort orders by priority
        sorted_orders = sorted(
            self.orders,
            key=lambda o: (o.priority.value, -o.width * o.height),
            reverse=False
        )
        
        # Get available sheets
        available_sheets = [
            s for s in self.sheets 
            if s.status == SheetStatus.AVAILABLE
        ]
        
        # Also consider remnants if strategy is efficiency
        if strategy == "efficiency":
            available_sheets.extend(self.remnants)
        
        # Sort sheets by size
        if strategy == "speed":
            available_sheets.sort(key=lambda s: s.total_area, reverse=True)
        else:
            available_sheets.sort(key=lambda s: s.total_area)
        
        # Assign orders to sheets
        for order in sorted_orders:
            if order.is_complete:
                continue
            
            # Find best sheet for this order
            best_sheet = self._find_best_sheet(order, available_sheets)
            
            if best_sheet:
                # Create or update job
                job = self._get_or_create_job(best_sheet, jobs)
                
                # Add order to job
                job.orders.append(order)
                order.assigned_sheet = best_sheet.sheet_id
                
                # Calculate how many can fit
                fit_count = self._calculate_fit_count(best_sheet, order)
                order.completed_quantity += min(fit_count, order.remaining_quantity)
                
                # Update sheet usage
                best_sheet.parts.append({
                    "order_id": order.order_id,
                    "width": order.width,
                    "height": order.height,
                    "quantity": fit_count
                })
                best_sheet.used_area += order.width * order.height * fit_count
        
        # Create jobs for sheets with assignments
        for sheet in available_sheets:
            if sheet.parts:
                job = CuttingJob(
                    job_id=f"JOB-{len(jobs)+1:03d}",
                    sheet=sheet,
                    orders=[o for o in self.orders if o.assigned_sheet == sheet.sheet_id],
                    nesting_result={"utilization": sheet.utilization},
                    estimated_time=self._estimate_cutting_time(sheet)
                )
                jobs.append(job)
        
        self.jobs = jobs
        return jobs
    
    def _find_best_sheet(self, order: CuttingOrder, sheets: List[GlassSheet]) -> Optional[GlassSheet]:
        """Find best sheet for order"""
        for sheet in sheets:
            if self._can_fit_order(sheet, order):
                return sheet
        return None
    
    def _can_fit_order(self, sheet: GlassSheet, order: CuttingOrder) -> bool:
        """Check if order can fit in sheet"""
        required_area = order.width * order.height * order.remaining_quantity
        return sheet.remaining_area >= required_area * 0.9  # 90% tolerance
    
    def _calculate_fit_count(self, sheet: GlassSheet, order: CuttingOrder) -> int:
        """Calculate how many orders can fit"""
        sheet_area = sheet.remaining_area
        part_area = order.width * order.height
        return min(
            int(sheet_area / part_area),
            order.remaining_quantity
        )
    
    def _get_or_create_job(self, sheet: GlassSheet, jobs: List[CuttingJob]) -> CuttingJob:
        """Get existing job or create new one"""
        for job in jobs:
            if job.sheet.sheet_id == sheet.sheet_id:
                return job
        
        job = CuttingJob(
            job_id=f"JOB-{len(jobs)+1:03d}",
            sheet=sheet,
            orders=[],
            nesting_result={}
        )
        jobs.append(job)
        return job
    
    def _estimate_cutting_time(self, sheet: GlassSheet) -> float:
        """Estimate cutting time in minutes"""
        # Rough estimate: 1 minute per part + setup time
        return len(sheet.parts) * 1.0 + 5.0
    
    def create_remnant(self, parent_sheet: GlassSheet, 
                       width: float, height: float) -> GlassSheet:
        """Create remnant from leftover sheet"""
        remnant = GlassSheet(
            sheet_id=f"REM-{parent_sheet.sheet_id}-{len(self.remnants)+1}",
            width=width,
            height=height,
            thickness=parent_sheet.thickness,
            glass_type=parent_sheet.glass_type,
            status=SheetStatus.REMNANT
        )
        self.remnants.append(remanent)
        return remnant
    
    def get_statistics(self) -> Dict:
        """Get batch statistics"""
        total_sheets = len(self.sheets)
        used_sheets = sum(1 for s in self.sheets if s.used_area > 0)
        total_orders = len(self.orders)
        completed_orders = sum(1 for o in self.orders if o.is_complete)
        
        avg_utilization = (
            sum(s.utilization for s in self.sheets if s.used_area > 0) / 
            max(used_sheets, 1)
        )
        
        return {
            "total_sheets": total_sheets,
            "used_sheets": used_sheets,
            "unused_sheets": total_sheets - used_sheets,
            "total_orders": total_orders,
            "completed_orders": completed_orders,
            "pending_orders": total_orders - completed_orders,
            "avg_utilization": avg_utilization,
            "total_jobs": len(self.jobs),
            "total_remnants": len(self.remnants)
        }


class CuttingQueue:
    """Manage cutting job queue"""
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path) if data_path else Path(__file__).parent.parent / 'data'
        self.queue_file = self.data_path / 'cutting_queue.json'
        self.jobs: List[CuttingJob] = []
        self.current_job: Optional[CuttingJob] = None
        self.completed_jobs: List[CuttingJob] = []
        
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.load()
    
    def load(self):
        """Load queue from file"""
        if self.queue_file.exists():
            with open(self.queue_file, 'r') as f:
                data = json.load(f)
                # TODO: Convert JSON back to objects
                self.jobs = []
    
    def save(self):
        """Save queue to file"""
        data = {
            "jobs": [j.to_dict() for j in self.jobs],
            "current_job": self.current_job.to_dict() if self.current_job else None,
            "completed_jobs": [j.to_dict() for j in self.completed_jobs[-100:]]
        }
        with open(self.queue_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_job(self, job: CuttingJob):
        """Add job to queue"""
        self.jobs.append(job)
        self.save()
    
    def start_next_job(self) -> Optional[CuttingJob]:
        """Start next job in queue"""
        if not self.jobs:
            return None
        
        job = self.jobs.pop(0)
        job.status = "processing"
        job.started_at = datetime.now()
        self.current_job = job
        self.save()
        
        return job
    
    def complete_job(self, actual_time: Optional[float] = None):
        """Complete current job"""
        if self.current_job:
            self.current_job.status = "completed"
            self.current_job.completed_at = datetime.now()
            if actual_time:
                self.current_job.actual_time = actual_time
            self.completed_jobs.append(self.current_job)
            self.current_job = None
            self.save()
    
    def get_queue_status(self) -> Dict:
        """Get queue status"""
        return {
            "pending_jobs": len(self.jobs),
            "current_job": self.current_job.job_id if self.current_job else None,
            "completed_today": sum(
                1 for j in self.completed_jobs 
                if j.completed_at and j.completed_at.date() == datetime.now().date()
            ),
            "total_completed": len(self.completed_jobs),
            "estimated_total_time": sum(j.estimated_time for j in self.jobs)
        }
    
    def prioritize_job(self, job_id: str, new_priority: OrderPriority):
        """Change job priority"""
        for job in self.jobs:
            if job.job_id == job_id:
                # Move to appropriate position in queue
                self.jobs.remove(job)
                insert_pos = 0
                for i, j in enumerate(self.jobs):
                    if j.orders and j.orders[0].priority.value <= new_priority.value:
                        insert_pos = i
                        break
                self.jobs.insert(insert_pos, job)
                self.save()
                break
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel job"""
        for i, job in enumerate(self.jobs):
            if job.job_id == job_id:
                job.status = "cancelled"
                self.jobs.pop(i)
                self.save()
                return True
        return False


def demo():
    """Demo usage"""
    print("=" * 60)
    print("Batch Processing Demo")
    print("=" * 60)
    
    # Create optimizer
    optimizer = BatchOptimizer()
    
    # Add sheets
    print("\n📦 Adding sheets...")
    for i in range(3):
        sheet = GlassSheet(
            sheet_id=f"SHEET-{i+1:03d}",
            width=6000,
            height=3000,
            thickness=4,
            glass_type="float"
        )
        optimizer.add_sheet(sheet)
        print(f"   Added: {sheet.sheet_id} ({sheet.width}x{sheet.height})")
    
    # Add orders
    print("\n📋 Adding orders...")
    orders_data = [
        {"order_id": "ORD-001", "width": 500, "height": 400, "quantity": 10, "priority": OrderPriority.HIGH},
        {"order_id": "ORD-002", "width": 300, "height": 200, "quantity": 20, "priority": OrderPriority.NORMAL},
        {"order_id": "ORD-003", "width": 800, "height": 600, "quantity": 5, "priority": OrderPriority.URGENT},
    ]
    
    for od in orders_data:
        order = CuttingOrder(**od)
        optimizer.add_order(order)
        print(f"   Added: {order.order_id} ({order.width}x{order.height} x{order.quantity})")
    
    # Optimize batch
    print("\n⚡ Optimizing batch...")
    jobs = optimizer.optimize_batch(strategy="efficiency")
    
    print(f"\n📊 Results:")
    print(f"   Jobs created: {len(jobs)}")
    print(f"   Sheets used: {sum(1 for j in jobs if j.orders)}")
    
    for job in jobs:
        print(f"\n   {job.job_id}:")
        print(f"      Sheet: {job.sheet.sheet_id}")
        print(f"      Orders: {len(job.orders)}")
        print(f"      Est. time: {job.estimated_time:.1f} min")
        print(f"      Utilization: {job.sheet.utilization*100:.1f}%")
    
    # Statistics
    print("\n📈 Statistics:")
    stats = optimizer.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # Queue management
    print("\n📋 Queue Management:")
    queue = CuttingQueue()
    
    for job in jobs:
        queue.add_job(job)
        print(f"   Added to queue: {job.job_id}")
    
    print(f"\n   Queue status: {queue.get_queue_status()}")


if __name__ == "__main__":
    demo()