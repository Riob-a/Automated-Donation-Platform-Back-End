from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'  # Corrected from _tablename_
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Store hashed password
    is_admin = db.Column(db.Boolean, default=False)
    donations = db.relationship('Donation', backref='donor', lazy=True)

    def __repr__(self):  # Corrected from _repr_
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin
        }

class Charity(db.Model):
    __tablename__ = 'charities'  # Corrected from _tablename_
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(200))
    approved = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(500))  # New field for image URL
    donations = db.relationship('Donation', backref='charity', lazy=True)
    beneficiaries = db.relationship('Beneficiary', backref='charity', lazy=True)

    def __repr__(self):  # Corrected from _repr_
        return f"<Charity {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'website': self.website,
            'approved': self.approved,
            'image_url': self.image_url
        }

class Donation(db.Model):
    __tablename__ = 'donations'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    anonymous = db.Column(db.Boolean, default=False)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.id'), nullable=False)

    def __repr__(self):
        return f"<Donation {self.amount} by User {self.user_id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'anonymous': self.anonymous,
            'donation_date': self.donation_date,
            'user_id': self.user_id,
            'charity_id': self.charity_id
        }

class Beneficiary(db.Model):
    __tablename__ = 'beneficiaries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    story = db.Column(db.Text, nullable=True)
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.id'), nullable=False)

    def __repr__(self):
        return f"<Beneficiary {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'story': self.story,
            'charity_id': self.charity_id
        }

class TokenBlacklist(db.Model):
    __tablename__ = 'token_blacklist'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<TokenBlacklist {self.token}>"