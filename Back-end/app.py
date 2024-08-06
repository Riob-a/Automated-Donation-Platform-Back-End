from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
import bcrypt
import os

from models import db, User, Charity, Donation, Beneficiary

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///App.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

BLACKLIST = set()

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in BLACKLIST

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Automated Donation Platform"}), 200

# User Routes
@app.route('/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'msg': 'Email already in use'}), 400

    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    new_user = User(
        username=data['username'],
        email=data['email'],
        password=hashed_password.decode('utf-8')
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict()), 201

@app.route('/users/login', methods=['POST'])
def login_user():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
        access_token = create_access_token(identity={'id': user.id, 'username': user.username})
        return jsonify(access_token=access_token), 200
    return jsonify({'msg': 'Invalid email or password'}), 401

@app.route('/users/protected', methods=['GET'])
@jwt_required()
def protected_user():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    BLACKLIST.add(jti)
    return jsonify(msg="Logout successful"), 200

# Charity Routes
@app.route('/charities', methods=['GET'])
def list_charities():
    charities = Charity.query.filter_by(approved=True).all()
    return jsonify([charity.to_dict() for charity in charities]), 200

@app.route('/charities', methods=['POST'])
def create_charity():
    data = request.get_json()
    new_charity = Charity(
        name=data['name'],
        description=data['description'],
        website=data.get('website')
    )
    db.session.add(new_charity)
    db.session.commit()
    return jsonify(new_charity.to_dict()), 201

@app.route('/charities/<int:charity_id>', methods=['GET'])
def get_charity(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    return jsonify(charity.to_dict()), 200

@app.route('/charities/<int:charity_id>', methods=['PATCH'])
def update_charity(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    data = request.get_json()
    if 'name' in data:
        charity.name = data['name']
    if 'description' in data:
        charity.description = data['description']
    if 'website' in data:
        charity.website = data['website']
    if 'approved' in data:
        charity.approved = data['approved']
    db.session.commit()
    return jsonify(charity.to_dict()), 200

@app.route('/charities/<int:charity_id>', methods=['DELETE'])
def delete_charity(charity_id):
    charity = Charity.query.get_or_404(charity_id)
    db.session.delete(charity)
    db.session.commit()
    return '', 204

# Donation Routes
@app.route('/donations', methods=['POST'])
def create_donation():
    data = request.get_json()
    new_donation = Donation(
        amount=data['amount'],
        anonymous=data.get('anonymous', False),
        user_id=data['user_id'],
        charity_id=data['charity_id']
    )
    db.session.add(new_donation)
    db.session.commit()
    return jsonify(new_donation.to_dict()), 201

@app.route('/donations/<int:donation_id>', methods=['GET'])
def get_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    return jsonify(donation.to_dict()), 200

@app.route('/donations/<int:donation_id>', methods=['DELETE'])
def delete_donation(donation_id):
    donation = Donation.query.get_or_404(donation_id)
    db.session.delete(donation)
    db.session.commit()
    return '', 204

# Beneficiary Routes
@app.route('/beneficiaries', methods=['POST'])
def create_beneficiary():
    data = request.get_json()
    new_beneficiary = Beneficiary(
        name=data['name'],
        story=data.get('story'),
        charity_id=data['charity_id']
    )
    db.session.add(new_beneficiary)
    db.session.commit()
    return jsonify(new_beneficiary.to_dict()), 201

@app.route('/beneficiaries/<int:beneficiary_id>', methods=['GET'])
def get_beneficiary(beneficiary_id):
    beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
    return jsonify(beneficiary.to_dict()), 200

@app.route('/beneficiaries/<int:beneficiary_id>', methods=['PATCH'])
def update_beneficiary(beneficiary_id):
    beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
    data = request.get_json()
    if 'name' in data:
        beneficiary.name = data['name']
    if 'story' in data:
        beneficiary.story = data['story']
    db.session.commit()
    return jsonify(beneficiary.to_dict()), 200

@app.route('/beneficiaries/<int:beneficiary_id>', methods=['DELETE'])
def delete_beneficiary(beneficiary_id):
    beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
    db.session.delete(beneficiary)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
    
