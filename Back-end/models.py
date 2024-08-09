from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Store hashed password
    is_admin = db.Column(db.Boolean, default=False)
    donations = db.relationship('Donation', backref='donor', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin
        }

class Charity(db.Model):
    __tablename__ = 'charities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(200))
    image_url = db.Column(db.String(500))  # Field for image URL
    donations = db.relationship('Donation', backref='charity', lazy=True, passive_deletes=True)
    beneficiaries = db.relationship('Beneficiary', backref='charity', lazy=True, passive_deletes=True)

    def __repr__(self):
        return f"<Charity {self.name}>"

    def to_dict(self):
        total_donations = sum(donation.amount for donation in self.donations)
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'website': self.website,
            'image_url': self.image_url,
            'total_donations': total_donations
        }
    
class UnapprovedCharity(db.Model):
    __tablename__ = 'unapproved_charities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(200))
    image_url = db.Column(db.String(500))  # Field for image URL
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UnapprovedCharity {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'website': self.website,
            'image_url': self.image_url,
            'date_submitted': self.date_submitted
        }

class Donation(db.Model):
    __tablename__ = 'donations'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    anonymous = db.Column(db.Boolean, default=False)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)#set to true after testing
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.id', ondelete='SET NULL'), nullable=True)

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
    image_url = db.Column(db.String(500))
    charity_id = db.Column(db.Integer, db.ForeignKey('charities.id', ondelete='SET NULL'), nullable=True)

    def __repr__(self):
        return f"<Beneficiary {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'story': self.story,
            'image_url':self.image_url,
            'charity_id': self.charity_id
        }

class TokenBlacklist(db.Model):
    __tablename__ = 'token_blacklist'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    
    def __repr__(self):
        return f"<TokenBlacklist {self.token}>"
    
class Application(db.Model):
    __tablename__ = 'applications'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    website = db.Column(db.String(200))
    image_url = db.Column(db.String(500))
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Pending')  # Can be 'Pending', 'Approved', 'Rejected'

    def __repr__(self):
        return f"<Application {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'website': self.website,
            'image_url': self.image_url,
            'date_submitted': self.date_submitted,
            'status': self.status
        }

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Store hashed password

    def __repr__(self):
        return f"<Admin {self.username}>"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
        }

