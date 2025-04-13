from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """User model for escort accounts"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(10), default="escort")  # escort or admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with profile
    profile = db.relationship('Profile', backref='user', uselist=False)

    def __repr__(self):
        return f"<User {self.username}>"

class Profile(db.Model):
    """Profile model for escort details"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Profile fields
    nickname = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)  # in kg
    height = db.Column(db.Integer, nullable=False)  # in cm
    location = db.Column(db.String(100), nullable=False)
    
    # Verification status
    is_verified = db.Column(db.Boolean, default=False)
    is_rejected = db.Column(db.Boolean, default=False)
    verification_note = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with verification images
    verification_images = db.relationship('VerificationImage', backref='profile', lazy=True)

    def __repr__(self):
        return f"<Profile {self.nickname}>"

class VerificationImage(db.Model):
    """Model for escort verification images"""
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    
    # File info
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<VerificationImage {self.filename}>"
