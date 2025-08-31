from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
import bcrypt
import hashlib
import secrets

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    middle_initial = db.Column(db.String(1), nullable=True)
    hospital_name = db.Column(db.String(100), nullable=False)
    hospital_room_no = db.Column(db.String(20), nullable=False)
    profile_picture = db.Column(db.Text, nullable=True)  # Base64 encoded image
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    remember_token = db.Column(db.String(255), nullable=True)
    
    # Relationships
    measurements = db.relationship('Measurement', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def generate_profile_picture(self):
        """Generate a 64x64 circle profile picture based on username"""
        from utils import generate_avatar
        # Generate the actual avatar image as base64 data
        self.profile_picture = generate_avatar(self.username)
    
    def set_remember_token(self):
        """Generate and set a secure remember token"""
        self.remember_token = secrets.token_urlsafe(32)
        return self.remember_token
    
    def clear_remember_token(self):
        """Clear the remember token"""
        self.remember_token = None
    
    @property
    def full_name(self):
        """Get full name"""
        if self.middle_initial:
            return f"{self.first_name} {self.middle_initial}. {self.surname}"
        return f"{self.first_name} {self.surname}"
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'hospital_name': self.hospital_name,
            'hospital_room_no': self.hospital_room_no,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Measurement(db.Model):
    __tablename__ = 'measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    point_name = db.Column(db.String(50), nullable=False)  # e.g., "Right Heel", "Left Big Toe"
    vpt_voltage = db.Column(db.Float, nullable=True)  # Vibration Perception Threshold in Volts
    temperature = db.Column(db.Float, nullable=True)  # Temperature in Celsius
    spo2 = db.Column(db.Integer, nullable=True)  # SpO2 percentage
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.Text, nullable=True)  # Optional notes for this measurement
    is_valid = db.Column(db.Boolean, default=True)  # Flag for data validity
    
    def validate_data(self):
        """Validate measurement data ranges"""
        errors = []
        
        if self.vpt_voltage is not None:
            if not (0 <= self.vpt_voltage <= 50):
                errors.append("VPT voltage must be between 0-50V")
        
        if self.temperature is not None:
            if not (25 <= self.temperature <= 45):
                errors.append("Temperature must be between 25-45°C")
        
        if self.spo2 is not None:
            if not (70 <= self.spo2 <= 100):
                errors.append("SpO2 must be between 70-100%")
        
        self.is_valid = len(errors) == 0
        return errors
    
    @property
    def quality_score(self):
        """Calculate data quality score based on completeness and validity"""
        score = 0
        total_fields = 3
        
        if self.vpt_voltage is not None:
            score += 1
        if self.temperature is not None:
            score += 1
        if self.spo2 is not None:
            score += 1
        
        completeness = (score / total_fields) * 100
        validity_bonus = 10 if self.is_valid else -20
        
        return min(100, max(0, completeness + validity_bonus))
    
    def to_dict(self):
        """Convert measurement to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'point_name': self.point_name,
            'vpt_voltage': self.vpt_voltage,
            'temperature': self.temperature,
            'spo2': self.spo2,
            'timestamp': self.timestamp.isoformat(),
            'notes': self.notes,
            'is_valid': self.is_valid,
            'quality_score': self.quality_score
        }

class APIKey(db.Model):
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key_name = db.Column(db.String(100), nullable=False)
    key_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = db.Column(db.DateTime, nullable=True)
    usage_count = db.Column(db.Integer, default=0)
    
    @staticmethod
    def hash_key(api_key):
        """Hash an API key"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @classmethod
    def verify_key(cls, api_key):
        """Verify an API key"""
        key_hash = cls.hash_key(api_key)
        api_key_obj = cls.query.filter_by(key_hash=key_hash, is_active=True).first()
        if api_key_obj:
            api_key_obj.last_used = datetime.now(timezone.utc)
            api_key_obj.usage_count += 1
            db.session.commit()
            return True
        return False

# Predefined measurement points
MEASUREMENT_POINTS = {
    'right': [
        'Right Heel',
        'Right In Step', 
        'Right 5th MT',
        'Right 3rd MT',
        'Right 1st MT',
        'Right Big Toe'
    ],
    'left': [
        'Left Heel',
        'Left In Step',
        'Left 5th MT', 
        'Left 3rd MT',
        'Left 1st MT',
        'Left Big Toe'
    ]
}

# Chart color definitions for consistent visualization
CHART_COLORS = {
    'right_heel': '#ef4444',      # Red
    'right_instep': '#f59e0b',    # Amber  
    'right_5th_mt': '#3b82f6',    # Blue
    'right_3rd_mt': '#10b981',    # Emerald
    'right_1st_mt': '#8b5cf6',    # Violet
    'right_big_toe': '#f97316',   # Orange
    'left_heel': '#dc2626',       # Red-600
    'left_instep': '#d97706',     # Amber-600
    'left_5th_mt': '#2563eb',     # Blue-600
    'left_3rd_mt': '#059669',     # Emerald-600
    'left_1st_mt': '#7c3aed',     # Violet-600
    'left_big_toe': '#ea580c',    # Orange-600
    'temperature': '#ef4444',     # Red for temperature
    'spo2': '#8b5cf6'            # Violet for SpO2
}
