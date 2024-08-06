from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
import bcrypt
import os
from flasgger import Swagger
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
swagger = Swagger(app)  # Initialize Swagger

BLACKLIST = set()

@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in BLACKLIST

@app.route('/')
def home():
    """
    Welcome to the Automated Donation Platform
    ---
    responses:
      200:
        description: A welcome message
    """
    return jsonify({"message": "Welcome to the Automated Donation Platform"}), 200

# User Routes
@app.route('/users/register', methods=['POST'])
def register_user():
    """
    Register a new user
    ---
    parameters:
      - in: body
        name: user
        description: The user to create
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: johndoe
            email:
              type: string
              example: johndoe@example.com
            password:
              type: string
              example: secret
    responses:
      201:
        description: User created successfully
      400:
        description: Email already in use
    """
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
    """
    User login
    ---
    parameters:
      - in: body
        name: credentials
        description: User login credentials
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: johndoe@example.com
            password:
              type: string
              example: secret
    responses:
      200:
        description: Login successful
      401:
        description: Invalid email or password
    """
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
        access_token = create_access_token(identity={'id': user.id, 'username': user.username})
        return jsonify(access_token=access_token), 200
    return jsonify({'msg': 'Invalid email or password'}), 401

@app.route('/users/protected', methods=['GET'])
@jwt_required()
def protected_user():
    """
    Protected user route
    ---
    responses:
      200:
        description: Returns the identity of the logged-in user
        schema:
          type: object
          properties:
            logged_in_as:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
    """
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# Logout Route
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Log out a user
    ---
    responses:
      200:
        description: Logout successful
    """
    jti = get_jwt()['jti']
    BLACKLIST.add(jti)
    return jsonify(msg="Logout successful"), 200

# Charity Routes
@app.route('/charities', methods=['GET'])
def list_charities():
    """
    List all approved charities
    ---
    responses:
      200:
        description: A list of approved charities
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              description:
                type: string
              website:
                type: string
              approved:
                type: boolean
              image_url:
                type: string
    """
    charities = Charity.query.filter_by(approved=True).all()
    return jsonify([charity.to_dict() for charity in charities]), 200

@app.route('/charities', methods=['POST'])
def create_charity():
    """
    Create a new charity
    ---
    parameters:
      - in: body
        name: charity
        description: The charity to create
        schema:
          type: object
          required:
            - name
            - description
          properties:
            name:
              type: string
              example: "Charity Name"
            description:
              type: string
              example: "Description of the charity"
            website:
              type: string
              example: "https://www.charitywebsite.org"
            image_url:
              type: string
              example: "https://www.example.com/image.jpg"
    responses:
      201:
        description: Charity created successfully
    """
    data = request.get_json()
    new_charity = Charity(
        name=data['name'],
        description=data['description'],
        website=data.get('website'),
        image_url=data.get('image_url')
    )
    db.session.add(new_charity)
    db.session.commit()
    return jsonify(new_charity.to_dict()), 201

@app.route('/charities/<int:charity_id>', methods=['GET'])
def get_charity(charity_id):
    """
    Get details of a specific charity
    ---
    parameters:
      - in: path
        name: charity_id
        required: true
        description: ID of the charity
        type: integer
    responses:
      200:
        description: Charity details
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            description:
              type: string
            website:
              type: string
            approved:
              type: boolean
            image_url:
              type: string
    """
    charity = Charity.query.get_or_404(charity_id)
    return jsonify(charity.to_dict()), 200

@app.route('/charities/<int:charity_id>', methods=['PATCH'])
def update_charity(charity_id):
    """
    Update a charity
    ---
    parameters:
      - in: path
        name: charity_id
        required: true
        description: ID of the charity
        type: integer
      - in: body
        name: charity
        description: The charity details to update
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Updated Charity Name"
            description:
              type: string
              example: "Updated description of the charity"
            website:
              type: string
              example: "https://www.updatedwebsite.org"
            approved:
              type: boolean
            image_url:
              type: string
              example: "https://www.example.com/updated_image.jpg"
    responses:
      200:
        description: Charity updated successfully
    """
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
    if 'image_url' in data:
        charity.image_url = data['image_url']
    db.session.commit()
    return jsonify(charity.to_dict()), 200

@app.route('/charities/<int:charity_id>', methods=['DELETE'])
def delete_charity(charity_id):
    """
    Delete a charity
    ---
    parameters:
      - in: path
        name: charity_id
        required: true
        description: ID of the charity to delete
        type: integer
    responses:
      204:
        description: Charity deleted successfully
    """
    charity = Charity.query.get_or_404(charity_id)
    db.session.delete(charity)
    db.session.commit()
    return '', 204

# Donation Routes
@app.route('/donations', methods=['POST'])
def create_donation():
    """
    Create a new donation
    ---
    parameters:
      - in: body
        name: donation
        description: The donation to create
        schema:
          type: object
          required:
            - amount
            - user_id
            - charity_id
          properties:
            amount:
              type: number
              format: float
              example: 100.50
            anonymous:
              type: boolean
              example: false
            user_id:
              type: integer
              example: 1
            charity_id:
              type: integer
              example: 1
    responses:
      201:
        description: Donation created successfully
    """
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
    """
    Get details of a specific donation
    ---
    parameters:
      - in: path
        name: donation_id
        required: true
        description: ID of the donation
        type: integer
    responses:
      200:
        description: Donation details
        schema:
          type: object
          properties:
            id:
              type: integer
            amount:
              type: number
              format: float
            anonymous:
              type: boolean
            user_id:
              type: integer
            charity_id:
              type: integer
            timestamp:
              type: string
    """
    donation = Donation.query.get_or_404(donation_id)
    return jsonify(donation.to_dict()), 200

@app.route('/donations', methods=['GET'])
def list_donations():
    """
    List all donations
    ---
    responses:
      200:
        description: A list of all donations
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              amount:
                type: number
                format: float
              anonymous:
                type: boolean
              user_id:
                type: integer
              charity_id:
                type: integer
              timestamp:
                type: string
    """
    donations = Donation.query.all()
    return jsonify([donation.to_dict() for donation in donations]), 200

@app.route('/donations/<int:donation_id>', methods=['DELETE'])
def delete_donation(donation_id):
    """
    Delete a donation
    ---
    parameters:
      - in: path
        name: donation_id
        required: true
        description: ID of the donation to delete
        type: integer
    responses:
      204:
        description: Donation deleted successfully
    """
    donation = Donation.query.get_or_404(donation_id)
    db.session.delete(donation)
    db.session.commit()
    return '', 204

# Beneficiary Routes
@app.route('/beneficiaries', methods=['GET'])
def list_beneficiaries():
    """
    List all beneficiaries
    ---
    responses:
      200:
        description: A list of all beneficiaries
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              school:
                type: string
              supplies_needed:
                type: string
              status:
                type: string
    """
    beneficiaries = Beneficiary.query.all()
    return jsonify([beneficiary.to_dict() for beneficiary in beneficiaries]), 200

@app.route('/beneficiaries', methods=['POST'])
def create_beneficiary():
    """
    Create a new beneficiary
    ---
    parameters:
      - in: body
        name: beneficiary
        description: The beneficiary to create
        schema:
          type: object
          required:
            - name
            - school
          properties:
            name:
              type: string
              example: "Jane Doe"
            school:
              type: string
              example: "School Name"
            supplies_needed:
              type: string
              example: "Sanitary towels"
            status:
              type: string
              example: "Pending"
    responses:
      201:
        description: Beneficiary created successfully
    """
    data = request.get_json()
    new_beneficiary = Beneficiary(
        name=data['name'],
        school=data['school'],
        supplies_needed=data.get('supplies_needed'),
        status=data.get('status', 'Pending')
    )
    db.session.add(new_beneficiary)
    db.session.commit()
    return jsonify(new_beneficiary.to_dict()), 201

@app.route('/beneficiaries/<int:beneficiary_id>', methods=['GET'])
def get_beneficiary(beneficiary_id):
    """
    Get details of a specific beneficiary
    ---
    parameters:
      - in: path
        name: beneficiary_id
        required: true
        description: ID of the beneficiary
        type: integer
    responses:
      200:
        description: Beneficiary details
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
            school:
              type: string
            supplies_needed:
              type: string
            status:
              type: string
    """
    beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
    return jsonify(beneficiary.to_dict()), 200

@app.route('/beneficiaries/<int:beneficiary_id>', methods=['PATCH'])
def update_beneficiary(beneficiary_id):
    """
    Update a beneficiary
    ---
    parameters:
      - in: path
        name: beneficiary_id
        required: true
        description: ID of the beneficiary
        type: integer
      - in: body
        name: beneficiary
        description: The beneficiary details to update
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Jane Smith"
            school:
              type: string
              example: "Updated School Name"
            supplies_needed:
              type: string
              example: "Updated supplies needed"
            status:
              type: string
              example: "Approved"
    responses:
      200:
        description: Beneficiary updated successfully
    """
    beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
    data = request.get_json()
    if 'name' in data:
        beneficiary.name = data['name']
    if 'school' in data:
        beneficiary.school = data['school']
    if 'supplies_needed' in data:
        beneficiary.supplies_needed = data['supplies_needed']
    if 'status' in data:
        beneficiary.status = data['status']
    db.session.commit()
    return jsonify(beneficiary.to_dict()), 200

@app.route('/beneficiaries/<int:beneficiary_id>', methods=['DELETE'])
def delete_beneficiary(beneficiary_id):
    """
    Delete a beneficiary
    ---
    parameters:
      - in: path
        name: beneficiary_id
        required: true
        description: ID of the beneficiary to delete
        type: integer
    responses:
      204:
        description: Beneficiary deleted successfully
    """
    beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
    db.session.delete(beneficiary)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
