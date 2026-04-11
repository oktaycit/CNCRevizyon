#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Module
SQLite database with SQLAlchemy ORM for glass cutting program

Tables:
    - users: User authentication
    - orders: Cutting orders
    - sheets: Glass sheets
    - cutting_history: Cutting records
    - defects: Detected defects
    - blades: Blade management
"""

from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

try:
    from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
    from sqlalchemy.orm import declarative_base, sessionmaker, relationship
    from sqlalchemy.pool import StaticPool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("Warning: SQLAlchemy not installed. Run: pip install sqlalchemy")

Base = declarative_base() if SQLALCHEMY_AVAILABLE else object


# ==================== Database Models ====================

class User(Base):
    """User table"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100))
    role = Column(String(20), default='operator')  # admin, operator, viewer
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    orders = relationship("Order", back_populates="user")
    cutting_history = relationship("CuttingHistory", back_populates="user")
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active
        }


class Order(Base):
    """Orders table"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String(50), unique=True, nullable=False, index=True)
    customer = Column(String(100))
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    thickness = Column(Float, default=4.0)
    glass_type = Column(String(50), default='float')  # float, laminated, tempered
    priority = Column(Integer, default=2)  # 1=high, 2=normal, 3=low
    rotate_allowed = Column(Boolean, default=True)
    grinding_allowance = Column(String(50), default='none')
    notes = Column(Text)
    status = Column(String(20), default='pending')  # pending, cutting, completed, cancelled
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    cutting_history = relationship("CuttingHistory", back_populates="order")
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'customer': self.customer,
            'width': self.width,
            'height': self.height,
            'quantity': self.quantity,
            'thickness': self.thickness,
            'glass_type': self.glass_type,
            'priority': self.priority,
            'rotate_allowed': self.rotate_allowed,
            'grinding_allowance': self.grinding_allowance,
            'notes': self.notes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Sheet(Base):
    """Glass sheets table"""
    __tablename__ = 'sheets'
    
    id = Column(Integer, primary_key=True)
    sheet_id = Column(String(50), unique=True, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    thickness = Column(Float)
    glass_type = Column(String(50))
    supplier = Column(String(100))
    batch_number = Column(String(50))
    purchase_date = Column(DateTime)
    cost = Column(Float)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    cutting_history = relationship("CuttingHistory", back_populates="sheet")
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'sheet_id': self.sheet_id,
            'width': self.width,
            'height': self.height,
            'thickness': self.thickness,
            'glass_type': self.glass_type,
            'supplier': self.supplier,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class CuttingHistory(Base):
    """Cutting history table"""
    __tablename__ = 'cutting_history'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    sheet_id = Column(Integer, ForeignKey('sheets.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    utilization = Column(Float)  # 0.0 - 1.0
    waste_area = Column(Float)  # mm²
    total_cuts = Column(Integer)
    cutting_time = Column(Float)  # minutes
    gcode_file = Column(String(255))
    report_file = Column(String(255))
    algorithm = Column(String(50))  # guillotine, genetic, etc.
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    order = relationship("Order", back_populates="cutting_history")
    sheet = relationship("Sheet", back_populates="cutting_history")
    user = relationship("User", back_populates="cutting_history")
    defects = relationship("Defect", back_populates="cutting_history")
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'sheet_id': self.sheet_id,
            'user_id': self.user_id,
            'utilization': self.utilization,
            'waste_area': self.waste_area,
            'total_cuts': self.total_cuts,
            'cutting_time': self.cutting_time,
            'algorithm': self.algorithm,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Defect(Base):
    """Defects table"""
    __tablename__ = 'defects'
    
    id = Column(Integer, primary_key=True)
    cutting_history_id = Column(Integer, ForeignKey('cutting_history.id'), nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    defect_type = Column(String(50), nullable=False)  # scratch, bubble, crack, inclusion
    severity = Column(Float, default=0.5)  # 0.0 - 1.0
    radius = Column(Float)  # mm
    avoided = Column(Boolean, default=False)  # Whether cutting avoided this defect
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    cutting_history = relationship("CuttingHistory", back_populates="defects")
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'cutting_history_id': self.cutting_history_id,
            'x': self.x,
            'y': self.y,
            'defect_type': self.defect_type,
            'severity': self.severity,
            'radius': self.radius,
            'avoided': self.avoided,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# ==================== Database Manager ====================

class DatabaseManager:
    """Manage database operations"""
    
    def __init__(self, db_path: str = 'sqlite:///glass_cutting.db'):
        """
        Initialize database
        
        Args:
            db_path: Database path (SQLite or other)
        """
        if not SQLALCHEMY_AVAILABLE:
            self.engine = None
            self.Session = None
            return
        
        # Create engine
        self.engine = create_engine(
            db_path,
            poolclass=StaticPool,  # For SQLite
            echo=False
        )
        
        # Create tables
        Base.metadata.create_all(self.engine)
        
        # Create session factory
        Session = sessionmaker(bind=self.engine)
        self.Session = Session
    
    def get_session(self):
        """Get database session"""
        if self.Session:
            return self.Session()
        return None
    
    # User operations
    def create_user(self, username: str, password_hash: str, 
                    email: str = '', role: str = 'operator') -> Optional[User]:
        """Create new user"""
        if not self.Session:
            return None
        
        session = self.get_session()
        try:
            user = User(
                username=username,
                password_hash=password_hash,
                email=email,
                role=role
            )
            session.add(user)
            session.commit()
            return user
        finally:
            session.close()
    
    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        if not self.Session:
            return None
        
        session = self.get_session()
        try:
            return session.query(User).filter_by(username=username).first()
        finally:
            session.close()
    
    # Order operations
    def create_order(self, order_data: Dict, user_id: int = None) -> Optional[Order]:
        """Create new order"""
        if not self.Session:
            return None
        
        session = self.get_session()
        try:
            order = Order(
                order_id=order_data.get('order_id'),
                customer=order_data.get('customer'),
                width=float(order_data.get('width', 0)),
                height=float(order_data.get('height', 0)),
                quantity=int(order_data.get('quantity', 1)),
                thickness=float(order_data.get('thickness', 4)),
                glass_type=order_data.get('glass_type', 'float'),
                priority=int(order_data.get('priority', 2)),
                rotate_allowed=order_data.get('rotate_allowed', True),
                grinding_allowance=order_data.get('grinding_allowance', 'none'),
                notes=order_data.get('notes'),
                created_by=user_id
            )
            session.add(order)
            session.commit()
            return order
        finally:
            session.close()
    
    def get_orders(self, status: str = None, limit: int = 100) -> List[Order]:
        """Get orders with optional filter"""
        if not self.Session:
            return []
        
        session = self.get_session()
        try:
            query = session.query(Order)
            if status:
                query = query.filter_by(status=status)
            return query.order_by(Order.created_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    # Cutting history operations
    def record_cutting(self, data: Dict) -> Optional[CuttingHistory]:
        """Record cutting operation"""
        if not self.Session:
            return None
        
        session = self.get_session()
        try:
            history = CuttingHistory(
                order_id=data.get('order_id'),
                sheet_id=data.get('sheet_id'),
                user_id=data.get('user_id'),
                utilization=data.get('utilization'),
                waste_area=data.get('waste_area'),
                total_cuts=data.get('total_cuts'),
                cutting_time=data.get('cutting_time'),
                gcode_file=data.get('gcode_file'),
                report_file=data.get('report_file'),
                algorithm=data.get('algorithm', 'guillotine')
            )
            session.add(history)
            session.commit()
            return history
        finally:
            session.close()
    
    # Statistics
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        if not self.Session:
            return {}
        
        session = self.get_session()
        try:
            return {
                'total_users': session.query(User).count(),
                'total_orders': session.query(Order).count(),
                'total_sheets': session.query(Sheet).count(),
                'total_cuttings': session.query(CuttingHistory).count(),
                'total_defects': session.query(Defect).count(),
                'avg_utilization': session.query(
                    CuttingHistory.utilization
                ).filter(CuttingHistory.utilization != None).scalar() or 0
            }
        finally:
            session.close()


def demo():
    """Demo usage"""
    print("=" * 60)
    print("Database Module Demo")
    print("=" * 60)
    
    if not SQLALCHEMY_AVAILABLE:
        print("\n❌ SQLAlchemy not installed!")
        print("   Run: pip install sqlalchemy")
        return
    
    # Initialize database
    db = DatabaseManager('sqlite:///demo.db')
    
    print("\n📊 Database initialized")
    
    # Create user
    print("\n👤 Creating user...")
    user = db.create_user(
        username='admin',
        password_hash='hashed_password_here',
        email='admin@example.com',
        role='admin'
    )
    if user:
        print(f"   Created: {user.username} ({user.role})")
    
    # Create order
    print("\n📦 Creating order...")
    order = db.create_order({
        'order_id': 'ORD-001',
        'customer': 'Test Customer',
        'width': 500,
        'height': 400,
        'quantity': 10,
        'thickness': 4,
        'glass_type': 'float',
        'priority': 1
    }, user_id=user.id if user else None)
    
    if order:
        print(f"   Created: {order.order_id} - {order.width}x{order.height}mm")
    
    # Get orders
    print("\n📋 Getting orders...")
    orders = db.get_orders(limit=10)
    print(f"   Found {len(orders)} orders")
    
    # Statistics
    print("\n📈 Statistics:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    demo()