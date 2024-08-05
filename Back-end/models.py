from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    _tablename_ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Store hashed password
    is_admin = db.Column(db.Boolean, default=False)
    donations = db.relationship('Donation', backref='donor', lazy=True)

    def _repr_(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin
        }

class Charity(db.Model):
    _tablename_ = 'charities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(200))
    approved = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(500))  # New field for image URL
    donations = db.relationship('Donation', backref='charity', lazy=True)
    beneficiaries = db.relationship('Beneficiary', backref='charity', lazy=True)

    def _repr_(self):
        return f"<Charity {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'website': self.website,
            'approved': self.approved,
            'image_url': self.image_url
