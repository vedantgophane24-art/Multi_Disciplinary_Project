from datetime import datetime, timezone
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# The @login_manager.user_loader decorator registers this function with Flask-Login
@login_manager.user_loader
def load_user(id):
    """Flask-Login callback to load a user from session."""
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    """
    User database model.
    Includes UserMixin for Flask-Login integration.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256)) # Increased length for stronger hashes
    
    # User's total tracked stats
    total_waste_diverted_kg = db.Column(db.Float, default=0.0)
    
    # Defines the relationship to the Donation model
    donations = db.relationship('Donation', backref='donator', lazy='dynamic')

    def set_password(self, password):
        """Hashes and stores the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Donation(db.Model):
    """Model for a single donation (clothes OR money)."""
    id = db.Column(db.Integer, primary_key=True)
    donation_type = db.Column(db.String(50), index=True, nullable=False) # 'Clothes', 'Money', etc.
    
    # --- PHYSICAL DONATION FIELDS ---
    estimated_weight_kg = db.Column(db.Float, nullable=True) 

    # --- MONEY DONATION FIELDS ---
    amount = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(3), nullable=True) # 'INR', 'USD', etc.

    # --- IMAGE & AI FIELDS ---
    image_filename = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(10), nullable=True) # <-- THIS IS THE MISSING LINE
    # -------------------------

    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ngo_id = db.Column(db.Integer, db.ForeignKey('ngo.id'), nullable=False)

    def __repr__(self):
        if self.donation_type == 'Money':
            return f'<Donation {self.id}: {self.amount} {self.currency}>'
        return f'<Donation {self.id}: {self.estimated_weight_kg}kg of {self.donation_type}>'

class NGO(db.Model):
    """
    NGO / Collection Center database model.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, nullable=False)
    address = db.Column(db.String(250), nullable=False)
    latitude = db.Column(db.Float) # For mapping
    longitude = db.Column(db.Float) # For mapping
    phone = db.Column(db.String(20), nullable=True)
    
    # This creates the 'donation.ngo' attribute
    donations = db.relationship('Donation', backref='ngo', lazy='dynamic')

    def __repr__(self):
        return f'<NGO {self.name}>'

