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
    sessions = db.relationship('Session', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def generate_profile_picture(self):
        """Generate a 64x64 circle profile picture based on username"""
        # Create a simple avatar based on username hash
        username_hash = hashlib.md5(self.username.encode()).hexdigest()
        # This will be implemented with Pillow to create actual image
        # For now, we'll store the hash and generate image in the route
        self.profile_picture = username_hash
    
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

class Session(db.Model):
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_name = db.Column(db.String(100), nullable=False)
    session_type = db.Column(db.String(50), default='manual')  # manual, auto, template
    protocol = db.Column(db.String(50), nullable=True)  # diabetic_screening, quick_check, research
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled, paused
    plantar_pressure_status = db.Column(db.String(20), default='Unknown')  # Low, Normal, High
    notes = db.Column(db.Text, nullable=True)
    expected_points = db.Column(db.JSON, nullable=True)  # List of expected measurement points
    
    # Relationships
    measurements = db.relationship('Measurement', backref='session', lazy=True, cascade='all, delete-orphan')
    
    @property
    def duration_minutes(self):
        """Calculate session duration in minutes"""
        if self.completed_at:
            return int((self.completed_at - self.created_at).total_seconds() / 60)
        else:
            return int((datetime.now(timezone.utc) - self.created_at).total_seconds() / 60)
    
    @property
    def progress_percentage(self):
        """Calculate completion percentage based on expected points"""
        if not self.expected_points:
            return 100 if self.measurements else 0
        
        completed_points = set(m.point_name for m in self.measurements)
        expected_set = set(self.expected_points)
        
        if not expected_set:
            return 100
        
        return int((len(completed_points) / len(expected_set)) * 100)
    
    @property
    def missing_points(self):
        """Get list of missing measurement points"""
        if not self.expected_points:
            return []
        
        completed_points = set(m.point_name for m in self.measurements)
        expected_set = set(self.expected_points)
        
        return list(expected_set - completed_points)
    
    def is_point_measured(self, point_name):
        """Check if a specific point has been measured"""
        return any(m.point_name == point_name for m in self.measurements)
    
    def get_latest_measurement_for_point(self, point_name):
        """Get the most recent measurement for a specific point"""
        measurements = [m for m in self.measurements if m.point_name == point_name]
        return max(measurements, key=lambda x: x.timestamp) if measurements else None
    
    def mark_complete(self):
        """Mark session as completed"""
        self.status = 'completed'
        self.completed_at = datetime.now(timezone.utc)
        
        # Auto-determine plantar pressure status based on measurements
        if self.measurements:
            avg_vpt = sum(m.vpt_voltage for m in self.measurements if m.vpt_voltage) / len([m for m in self.measurements if m.vpt_voltage])
            if avg_vpt < 3.0:
                self.plantar_pressure_status = 'Low'
            elif avg_vpt > 7.0:
                self.plantar_pressure_status = 'High'
            else:
                self.plantar_pressure_status = 'Normal'
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'session_name': self.session_name,
            'session_type': self.session_type,
            'protocol': self.protocol,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'status': self.status,
            'plantar_pressure_status': self.plantar_pressure_status,
            'notes': self.notes,
            'measurement_count': len(self.measurements),
            'duration_minutes': self.duration_minutes,
            'progress_percentage': self.progress_percentage,
            'missing_points': self.missing_points,
            'expected_points': self.expected_points
        }

class Measurement(db.Model):
    __tablename__ = 'measurements'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    point_name = db.Column(db.String(50), nullable=False)  # e.g., "Right Heel", "Left Big Toe"
    vpt_voltage = db.Column(db.Float, nullable=True)  # Vibration Perception Threshold in Volts
    temperature = db.Column(db.Float, nullable=True)  # Temperature in Celsius
    spo2 = db.Column(db.Integer, nullable=True)  # SpO2 percentage
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    notes = db.Column(db.Text, nullable=True)  # Optional notes for this measurement
    is_valid = db.Column(db.Boolean, default=True)  # Flag for data validity
    retry_count = db.Column(db.Integer, default=0)  # Number of retries for this point
    
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
            'session_id': self.session_id,
            'point_name': self.point_name,
            'vpt_voltage': self.vpt_voltage,
            'temperature': self.temperature,
            'spo2': self.spo2,
            'timestamp': self.timestamp.isoformat(),
            'notes': self.notes,
            'is_valid': self.is_valid,
            'retry_count': self.retry_count,
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

# Session protocols with predefined measurement point sets
SESSION_PROTOCOLS = {
    'diabetic_screening': {
        'name': 'Diabetic Foot Screening',
        'description': 'Comprehensive diabetic foot assessment protocol',
        'points': MEASUREMENT_POINTS['right'] + MEASUREMENT_POINTS['left'],
        'required_measurements': ['vpt_voltage', 'temperature'],
        'optional_measurements': ['spo2'],
        'estimated_duration': 15  # minutes
    },
    'quick_check': {
        'name': 'Quick Assessment',
        'description': 'Basic assessment of key pressure points',
        'points': [
            'Right Heel', 'Right Big Toe', 'Right 1st MT',
            'Left Heel', 'Left Big Toe', 'Left 1st MT'
        ],
        'required_measurements': ['vpt_voltage'],
        'optional_measurements': ['temperature', 'spo2'],
        'estimated_duration': 8
    },
    'research': {
        'name': 'Research Protocol',
        'description': 'Comprehensive measurement for research purposes',
        'points': MEASUREMENT_POINTS['right'] + MEASUREMENT_POINTS['left'],
        'required_measurements': ['vpt_voltage', 'temperature', 'spo2'],
        'optional_measurements': [],
        'estimated_duration': 20
    },
    'right_foot_only': {
        'name': 'Right Foot Assessment',
        'description': 'Assessment of right foot only',
        'points': MEASUREMENT_POINTS['right'],
        'required_measurements': ['vpt_voltage', 'temperature'],
        'optional_measurements': ['spo2'],
        'estimated_duration': 8
    },
    'left_foot_only': {
        'name': 'Left Foot Assessment',
        'description': 'Assessment of left foot only',
        'points': MEASUREMENT_POINTS['left'],
        'required_measurements': ['vpt_voltage', 'temperature'],
        'optional_measurements': ['spo2'],
        'estimated_duration': 8
    }
}
