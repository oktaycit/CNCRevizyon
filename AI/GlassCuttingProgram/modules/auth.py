#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Authentication Module
JWT-based user authentication for glass cutting program

Features:
- User registration
- Login/Logout
- JWT token generation
- Password hashing (bcrypt)
- Role-based access control
- Token refresh
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path
import json

try:
    import jwt  # PyJWT
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("Warning: PyJWT not installed. Run: pip install PyJWT")

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    print("Warning: bcrypt not installed. Run: pip install bcrypt")


# JWT Configuration
JWT_SECRET = secrets.token_hex(32)  # In production, use environment variable
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_HOURS = 24
JWT_REFRESH_EXPIRY_DAYS = 7


class User:
    """User object"""
    
    def __init__(self, id: int, username: str, email: str = '', 
                 role: str = 'operator', is_active: bool = True):
        self.id = id
        self.username = username
        self.email = email
        self.role = role
        self.is_active = is_active
        self.created_at = datetime.now()
        self.last_login = None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


class AuthManager:
    """Manage user authentication"""
    
    # Default admin credentials (change in production!)
    DEFAULT_ADMIN = {
        'username': 'admin',
        'password': 'admin123',  # Change this!
        'email': 'admin@localhost',
        'role': 'admin'
    }
    
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = Path(data_path) if data_path else Path(__file__).parent.parent / 'data'
        self.users_file = self.data_path / 'users.json'
        self.sessions_file = self.data_path / 'sessions.json'
        self.users: Dict[int, Dict] = {}
        self.sessions: Dict[str, Dict] = {}
        
        # Create data directory
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self.load()
        
        # Create default admin if no users exist
        if not self.users:
            self.create_default_admin()
    
    def load(self):
        """Load users and sessions from files"""
        # Load users
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                data = json.load(f)
                self.users = {int(k): v for k, v in data.get('users', {}).items()}
        
        # Load sessions
        if self.sessions_file.exists():
            with open(self.sessions_file, 'r') as f:
                self.sessions = json.load(f).get('sessions', {})
        
        # Clean expired sessions
        self._cleanup_sessions()
    
    def save(self):
        """Save users and sessions to files"""
        # Save users
        with open(self.users_file, 'w') as f:
            json.dump({'users': self.users}, f, indent=2)
        
        # Save sessions
        with open(self.sessions_file, 'w') as f:
            json.dump({'sessions': self.sessions}, f, indent=2)
    
    def _cleanup_sessions(self):
        """Remove expired sessions"""
        now = datetime.now()
        expired = [
            token for token, session in self.sessions.items()
            if datetime.fromisoformat(session['expires_at']) < now
        ]
        
        for token in expired:
            del self.sessions[token]
        
        if expired:
            self.save()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt or fallback to SHA-256"""
        if BCRYPT_AVAILABLE:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        else:
            # Fallback (less secure, for development only)
            return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        if BCRYPT_AVAILABLE:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        else:
            # Fallback
            return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed
    
    def create_default_admin(self):
        """Create default admin user"""
        admin = self.create_user(
            username=self.DEFAULT_ADMIN['username'],
            password=self.DEFAULT_ADMIN['password'],
            email=self.DEFAULT_ADMIN['email'],
            role=self.DEFAULT_ADMIN['role']
        )
        print(f"✅ Default admin created: {self.DEFAULT_ADMIN['username']} / {self.DEFAULT_ADMIN['password']}")
    
    def create_user(self, username: str, password: str, 
                    email: str = '', role: str = 'operator') -> Optional[User]:
        """Create new user"""
        # Check if username exists
        for user in self.users.values():
            if user['username'] == username:
                return None
        
        # Create user
        user_id = max(self.users.keys(), default=0) + 1
        user = {
            'id': user_id,
            'username': username,
            'password_hash': self._hash_password(password),
            'email': email,
            'role': role,
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'last_login': None
        }
        
        self.users[user_id] = user
        self.save()
        
        return User(
            id=user_id,
            username=username,
            email=email,
            role=role
        )
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user and generate JWT token
        
        Returns:
            Dict with access_token, refresh_token, user info
        """
        # Find user
        user = None
        for u in self.users.values():
            if u['username'] == username:
                user = u
                break
        
        if not user:
            return None
        
        # Verify password
        if not self._verify_password(password, user['password_hash']):
            return None
        
        # Check if active
        if not user.get('is_active', True):
            return None
        
        # Update last login
        user['last_login'] = datetime.now().isoformat()
        self.save()
        
        # Generate tokens
        access_token = self._generate_access_token(user)
        refresh_token = self._generate_refresh_token(user)
        
        # Store session
        self.sessions[access_token] = {
            'user_id': user['id'],
            'expires_at': (datetime.now() + timedelta(hours=JWT_EXPIRY_HOURS)).isoformat(),
            'refresh_token': refresh_token
        }
        self.save()
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role']
            }
        }
    
    def _generate_access_token(self, user: Dict) -> str:
        """Generate JWT access token"""
        if not JWT_AVAILABLE:
            # Fallback: simple token
            return secrets.token_urlsafe(32)
        
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'exp': datetime.now() + timedelta(hours=JWT_EXPIRY_HOURS),
            'iat': datetime.now(),
            'type': 'access'
        }
        
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def _generate_refresh_token(self, user: Dict) -> str:
        """Generate JWT refresh token"""
        if not JWT_AVAILABLE:
            return secrets.token_urlsafe(32)
        
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'exp': datetime.now() + timedelta(days=JWT_REFRESH_EXPIRY_DAYS),
            'iat': datetime.now(),
            'type': 'refresh'
        }
        
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return user info"""
        if token in self.sessions:
            session = self.sessions[token]
            if datetime.fromisoformat(session['expires_at']) > datetime.now():
                # Valid session
                user = self.users.get(session['user_id'])
                if user:
                    return {
                        'user_id': user['id'],
                        'username': user['username'],
                        'role': user['role']
                    }
        
        if not JWT_AVAILABLE:
            return None
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Check token type
            if payload.get('type') != 'access':
                return None
            
            # Check expiry
            if datetime.fromtimestamp(payload['exp']) < datetime.now():
                return None
            
            return {
                'user_id': payload['user_id'],
                'username': payload['username'],
                'role': payload['role']
            }
            
        except jwt.InvalidTokenError:
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """Generate new access token using refresh token"""
        if not JWT_AVAILABLE:
            return None
        
        try:
            payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            
            if payload.get('type') != 'refresh':
                return None
            
            # Get user
            user = self.users.get(payload['user_id'])
            if not user:
                return None
            
            # Generate new access token
            new_access_token = self._generate_access_token(user)
            
            # Store new session
            self.sessions[new_access_token] = {
                'user_id': user['id'],
                'expires_at': (datetime.now() + timedelta(hours=JWT_EXPIRY_HOURS)).isoformat(),
                'refresh_token': refresh_token
            }
            self.save()
            
            return {
                'access_token': new_access_token,
                'expires_in': JWT_EXPIRY_HOURS * 3600
            }
            
        except jwt.InvalidTokenError:
            return None
    
    def logout(self, token: str):
        """Logout user (invalidate token)"""
        if token in self.sessions:
            del self.sessions[token]
            self.save()
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        return User(
            id=user['id'],
            username=user['username'],
            email=user.get('email', ''),
            role=user.get('role', 'operator'),
            is_active=user.get('is_active', True)
        )
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        for user in self.users.values():
            if user['username'] == username:
                return User(
                    id=user['id'],
                    username=user['username'],
                    email=user.get('email', ''),
                    role=user.get('role', 'operator'),
                    is_active=user.get('is_active', True)
                )
        return None
    
    def update_user(self, user_id: int, **kwargs) -> Optional[User]:
        """Update user information"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        # Update allowed fields
        allowed_fields = ['email', 'role', 'is_active']
        for field, value in kwargs.items():
            if field in allowed_fields:
                user[field] = value
        
        self.save()
        
        return self.get_user(user_id)
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """Change user password"""
        user = self.users.get(user_id)
        if not user:
            return False
        
        # Verify old password
        if not self._verify_password(old_password, user['password_hash']):
            return False
        
        # Set new password
        user['password_hash'] = self._hash_password(new_password)
        self.save()
        
        return True
    
    def get_statistics(self) -> Dict:
        """Get user statistics"""
        roles = {}
        for user in self.users.values():
            role = user.get('role', 'operator')
            roles[role] = roles.get(role, 0) + 1
        
        return {
            'total_users': len(self.users),
            'active_users': sum(1 for u in self.users.values() if u.get('is_active', True)),
            'active_sessions': len(self.sessions),
            'users_by_role': roles
        }


def demo():
    """Demo usage"""
    print("=" * 60)
    print("Authentication Module Demo")
    print("=" * 60)
    
    # Create auth manager
    auth = AuthManager()
    
    print("\n📊 Statistics:")
    stats = auth.get_statistics()
    print(f"   Total users: {stats['total_users']}")
    print(f"   Active users: {stats['active_users']}")
    print(f"   Active sessions: {stats['active_sessions']}")
    
    # Login with admin
    print("\n🔐 Testing login...")
    result = auth.authenticate('admin', 'admin123')
    
    if result:
        print(f"   ✅ Login successful!")
        print(f"   User: {result['user']['username']} ({result['user']['role']})")
        print(f"   Token: {result['access_token'][:50]}...")
        
        # Verify token
        print("\n✓ Verifying token...")
        user_info = auth.verify_token(result['access_token'])
        if user_info:
            print(f"   ✅ Token valid: {user_info['username']}")
        
        # Logout
        print("\n🚪 Logging out...")
        auth.logout(result['access_token'])
        print("   ✅ Logged out")
    else:
        print("   ❌ Login failed")
    
    # Create new user
    print("\n👤 Creating new user...")
    new_user = auth.create_user(
        username='operator1',
        password='password123',
        email='operator@example.com',
        role='operator'
    )
    
    if new_user:
        print(f"   ✅ User created: {new_user.username}")
    else:
        print("   ❌ User creation failed (may already exist)")


if __name__ == "__main__":
    demo()