from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt, get_jwt_identity
import bcrypt
import os
from flasgger import Swagger
from models import db, User, Charity, Donation, Beneficiary, Application, Admin, UnapprovedCharity

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
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
    Home endpoint
    ---
    responses:
      200:
        description: Welcome message
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Welcome to the Automated Donation Platform
    """
    return jsonify({"message": "Welcome to the Automated Donation Platform"}), 200

# User Routes
@app.route('/users/register', methods=['POST'])
def register_user():
    """
    Register a new user
    ---
    parameters:
      - name: body
        in: body
        description: User registration information
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: john_doe
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: password123
    responses:
      201:
        description: User created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: john_doe
                email:
                  type: string
                  example: john@example.com
      400:
        description: Bad request, email already in use
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
    Login a user
    ---
    parameters:
      - name: body
        in: body
        description: User login information
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: john@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Successful login
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: 'Login successful'
      401:
        description: Invalid email or password
    """
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'message': 'Login successful'}), 200
    
    return jsonify({'msg': 'Invalid email or password'}), 401


# @app.route('/users/protected', methods=['GET'])
# @jwt_required()
# def protected_user():
#     """
#     Access protected user data
#     ---
#     responses:
#       200:
#         description: Successfully retrieved user data
#         content:
#           application/json:
#             schema:
#               type: object
#               properties:
#                 logged_in_as:
#                   type: object
#                   properties:
#                     id:
#                       type: integer
#                       example: 1
#                     username:
#                       type: string
#                       example: john_doe
#     """
#     current_user = get_jwt_identity()
#     return jsonify(logged_in_as=current_user), 200

# Logout Route
# @app.route('/logout', methods=['POST'])
# @jwt_required()
# def logout():
#     """
#     Logout a user
#     ---
#     responses:
#       200:
#         description: Logout successful
#         content:
#           application/json:
#             schema:
#               type: object
#               properties:
#                 msg:
#                   type: string
#                   example: Logout successful
#     """
#     jti = get_jwt()['jti']
#     BLACKLIST.add(jti)
#     return jsonify(msg="Logout successful"), 200

# Charity Routes
@app.route('/charities', methods=['GET'])
def list_charities():
    """
    List all approved charities
    ---
    responses:
      200:
        description: List of approved charities
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  name:
                    type: string
                    example: Charity A
                  description:
                    type: string
                    example: A description of Charity A
                  website:
                    type: string
                    example: http://charitya.org
                  image_url:
                    type: string
                    example: http://charitya.org/image.jpg
    """
    charities = Charity.query.all()  # Fetch all charities
    return jsonify([charity.to_dict() for charity in charities]), 200

@app.route('/charities', methods=['POST'])
def create_charity():
    """
    Create a new charity
    ---
    parameters:
      - name: body
        in: body
        description: Charity information
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Charity B
            description:
              type: string
              example: A description of Charity B
            website:
              type: string
              example: http://charityb.org
            image_url:
              type: string
              example: http://charityb.org/image.jpg
    responses:
      201:
        description: Charity created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 2
                name:
                  type: string
                  example: Charity B
                description:
                  type: string
                  example: A description of Charity B
                website:
                  type: string
                  example: http://charityb.org
                image_url:
                  type: string
                  example: http://charityb.org/image.jpg
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
      - name: charity_id
        in: path
        description: ID of the charity to retrieve
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Details of the charity
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Charity A
                description:
                  type: string
                  example: A description of Charity A
                website:
                  type: string
                  example: http://charitya.org
                image_url:
                  type: string
                  example: http://charitya.org/image.jpg
      404:
        description: Charity not found
    """
    charity = Charity.query.get_or_404(charity_id)
    return jsonify(charity.to_dict()), 200

@app.route('/charities/<int:charity_id>', methods=['PATCH'])
def update_charity(charity_id):
    """
    Update a charity
    ---
    parameters:
      - name: charity_id
        in: path
        description: ID of the charity to update
        required: true
        schema:
          type: integer
      - name: body
        in: body
        description: Updated charity information
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Charity A Updated
            description:
              type: string
              example: Updated description of Charity A
            website:
              type: string
              example: http://charitya-updated.org
            image_url:
              type: string
              example: http://charitya-updated.org/image.jpg
    responses:
      200:
        description: Charity updated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Charity A Updated
                description:
                  type: string
                  example: Updated description of Charity A
                website:
                  type: string
                  example: http://charitya-updated.org
                image_url:
                  type: string
                  example: http://charitya-updated.org/image.jpg
      404:
        description: Charity not found
    """
    charity = Charity.query.get_or_404(charity_id)
    data = request.get_json()
    if 'name' in data:
        charity.name = data['name']
    if 'description' in data:
        charity.description = data['description']
    if 'website' in data:
        charity.website = data['website']
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
      - name: charity_id
        in: path
        description: ID of the charity to delete
        required: true
        schema:
          type: integer
    responses:
      204:
        description: Charity deleted successfully
      404:
        description: Charity not found
    """
    charity = Charity.query.get(charity_id)
    if not charity:
        return jsonify({'msg': 'Charity not found'}), 404
    db.session.delete(charity)
    db.session.commit()
    return '', 204

# Unapproved charities
@app.route('/unapproved-charities', methods=['GET'])
def get_unapproved_charities():
    """
    Get a list of unapproved charities
    ---
    responses:
      200:
        description: A list of unapproved charities
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  name:
                    type: string
                    example: "Charity Name"
                  description:
                    type: string
                    example: "Charity Description"
                  website:
                    type: string
                    example: "https://www.charitywebsite.org"
                  image_url:
                    type: string
                    example: "https://www.example.com/image.jpg"
      500:
        description: Server error
    """
    try:
        unapproved_charities = UnapprovedCharity.query.all()
        result = [charity.to_dict() for charity in unapproved_charities]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/unapproved-charities', methods=['POST'])
def create_unapproved_charity():
    """
    Create a new unapproved charity
    ---
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                example: "Charity Name"
              description:
                type: string
                example: "Charity Description"
              website:
                type: string
                example: "https://www.charitywebsite.org"
              image_url:
                type: string
                example: "https://www.example.com/image.jpg"
    responses:
      201:
        description: Unapproved charity created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: "Charity Name"
                description:
                  type: string
                  example: "Charity Description"
                website:
                  type: string
                  example: "https://www.charitywebsite.org"
                image_url:
                  type: string
                  example: "https://www.example.com/image.jpg"
      400:
        description: Invalid input data
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ('name', 'description')):
            return jsonify({'error': 'Invalid input data'}), 400

        new_charity = UnapprovedCharity(
            name=data.get('name'),
            description=data.get('description'),
            website=data.get('website'),
            image_url=data.get('image_url')
        )
        db.session.add(new_charity)
        db.session.commit()

        return jsonify(new_charity.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/unapproved-charities/<int:id>', methods=['PATCH'])
def update_unapproved_charity_status(id):
    """
    Approve or reject an unapproved charity
    ---
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              status:
                type: string
                example: "Approved" or "Rejected"
    responses:
      200:
        description: Charity status updated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: "Charity Name"
                description:
                  type: string
                  example: "Charity Description"
                website:
                  type: string
                  example: "https://www.charitywebsite.org"
                image_url:
                  type: string
                  example: "https://www.example.com/image.jpg"
                status:
                  type: string
                  example: "Approved"
      400:
        description: Invalid input data
      404:
        description: Charity not found
      500:
        description: Server error
    """
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({'error': 'Invalid input data'}), 400

        unapproved_charity = UnapprovedCharity.query.get(id)
        if not unapproved_charity:
            return jsonify({'error': 'Charity not found'}), 404

        if data['status'] == 'Approved':
            new_charity = Charity(
                name=unapproved_charity.name,
                description=unapproved_charity.description,
                website=unapproved_charity.website,
                image_url=unapproved_charity.image_url
            )
            db.session.add(new_charity)
            db.session.delete(unapproved_charity)
            db.session.commit()
            return jsonify(new_charity.to_dict()), 200

        elif data['status'] == 'Rejected':
            db.session.delete(unapproved_charity)
            db.session.commit()
            return jsonify({'message': 'Application has been rejected!'}), 200

        else:
            return jsonify({'error': 'Invalid status'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
def move_unapproved_charities():
    try:
        # Retrieve all unapproved charities
        unapproved_charities = UnapprovedCharity.query.all()
        
        # Iterate through each unapproved charity
        for unapproved in unapproved_charities:
            # Create a new Charity instance
            new_charity = Charity(
                name=unapproved.name,
                description=unapproved.description,
                website=unapproved.website,
                image_url=unapproved.image_url
            )
            
            # Add the new charity to the database session
            db.session.add(new_charity)
            
            # Delete the unapproved charity from the UnapprovedCharity model
            db.session.delete(unapproved)
        
        # Commit the changes to the database
        db.session.commit()
        
        return jsonify({"message": "Charities have been approved successfully"}), 200
    
    except Exception as e:
        # Handle any exceptions and rollback changes if necessary
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
#Moves data from Unapproaved model to Charities model    
@app.route('/move-unapproved-charities', methods=['POST'])
def move_charities():
    """
    Move unapproved charities to the approved charities list
    ---
    responses:
      200:
        description: Unapproved charities moved successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Charities have been approved successfully"
      500:
        description: Server error
    """
    return move_unapproved_charities()

# Donation Routes
@app.route('/donations', methods=['POST'])
def create_donation():
    data = request.get_json()
    charity_id = data.get('charity_id')
    amount = data.get('amount')

    if not charity_id or not amount:
        return jsonify({'msg': 'Missing required fields'}), 400

    # Create and save the donation without user_id
    donation = Donation(charity_id=charity_id, amount=amount)
    db.session.add(donation)
    db.session.commit()

    return jsonify({'msg': 'Donation created successfully'}), 201


@app.route('/donations/<int:donation_id>', methods=['GET'])
def get_donation(donation_id):
    """
    Get details of a specific donation
    ---
    parameters:
      - name: donation_id
        in: path
        description: ID of the donation to retrieve
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Details of the donation
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                amount:
                  type: number
                  format: float
                  example: 50.0
                user_id:
                  type: integer
                  example: 1
                charity_id:
                  type: integer
                  example: 1
                anonymous:
                  type: boolean
                  example: false
      404:
        description: Donation not found
    """
    donation = Donation.query.get_or_404(donation_id)
    return jsonify(donation.to_dict()), 200

@app.route('/donations/<int:donation_id>', methods=['DELETE'])
def delete_donation(donation_id):
    """
    Delete a donation
    ---
    parameters:
      - name: donation_id
        in: path
        description: ID of the donation to delete
        required: true
        schema:
          type: integer
    responses:
      204:
        description: Donation deleted successfully
      404:
        description: Donation not found
    """
    donation = Donation.query.get(donation_id)
    if not donation:
        return jsonify({'msg': 'Donation not found'}), 404
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
        description: List of all beneficiaries
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  name:
                    type: string
                    example: Jane Doe
                  story:
                    type: string
                    example: A story about Jane Doe
                  image_url:
                    type: string
                    example: https://example.com/image.jpg
                  charity_id:
                    type: integer
                    example: 1
    """
    beneficiaries = Beneficiary.query.all()
    return jsonify([beneficiary.to_dict() for beneficiary in beneficiaries]), 200

@app.route('/beneficiaries', methods=['POST'])
def create_beneficiary():
    """
    Create a new beneficiary
    ---
    parameters:
      - name: body
        in: body
        description: Beneficiary information
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Jane Doe
            story:
              type: string
              example: A story about Jane Doe
            image_url:
              type: string
              example: https://example.com/image.jpg
            charity_id:
              type: integer
              example: 1
    responses:
      201:
        description: Beneficiary created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Jane Doe
                story:
                  type: string
                  example: A story about Jane Doe
                image_url:
                  type: string
                  example: https://example.com/image.jpg
                charity_id:
                  type: integer
                  example: 1
    """
    data = request.get_json()
    new_beneficiary = Beneficiary(
        name=data['name'],
        story=data.get('story', ''),
        image_url=data.get('image_url', ''),
        charity_id=data['charity_id']
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
      - name: beneficiary_id
        in: path
        description: ID of the beneficiary to retrieve
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Details of the beneficiary
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Jane Doe
                story:
                  type: string
                  example: A story about Jane Doe
                image_url:
                  type: string
                  example: https://example.com/image.jpg
                charity_id:
                  type: integer
                  example: 1
      404:
        description: Beneficiary not found
    """
    beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
    return jsonify(beneficiary.to_dict()), 200

@app.route('/beneficiaries/<int:beneficiary_id>', methods=['PATCH'])
def update_beneficiary(beneficiary_id):
    """
    Update a beneficiary
    ---
    parameters:
      - name: beneficiary_id
        in: path
        description: ID of the beneficiary to update
        required: true
        schema:
          type: integer
      - name: body
        in: body
        description: Updated beneficiary information
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Jane Doe Updated
            story:
              type: string
              example: Updated story about Jane Doe
            image_url:
              type: string
              example: https://example.com/updated-image.jpg
    responses:
      200:
        description: Beneficiary updated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Jane Doe Updated
                story:
                  type: string
                  example: Updated story about Jane Doe
                image_url:
                  type: string
                  example: https://example.com/updated-image.jpg
                charity_id:
                  type: integer
                  example: 1
      404:
        description: Beneficiary not found
    """
    beneficiary = Beneficiary.query.get_or_404(beneficiary_id)
    data = request.get_json()
    if 'name' in data:
        beneficiary.name = data['name']
    if 'story' in data:
        beneficiary.story = data['story']
    if 'image_url' in data:
        beneficiary.image_url = data['image_url']
    db.session.commit()
    return jsonify(beneficiary.to_dict()), 200

@app.route('/beneficiaries/<int:beneficiary_id>', methods=['DELETE'])
def delete_beneficiary(beneficiary_id):
    """
    Delete a beneficiary
    ---
    parameters:
      - name: beneficiary_id
        in: path
        description: ID of the beneficiary to delete
        required: true
        schema:
          type: integer
    responses:
      204:
        description: Beneficiary deleted successfully
      404:
        description: Beneficiary not found
    """
    beneficiary = Beneficiary.query.get(beneficiary_id)
    if not beneficiary:
        return jsonify({'msg': 'Beneficiary not found'}), 404
    db.session.delete(beneficiary)
    db.session.commit()
    return '', 204


# Application Routes
@app.route('/applications', methods=['GET'])
def list_applications():
    """
    List all applications
    ---
    responses:
      200:
        description: A list of all applications
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  name:
                    type: string
                    example: Application A
                  description:
                    type: string
                    example: Description of Application A
                  website:
                    type: string
                    example: http://applicationa.org
                  image_url:
                    type: string
                    example: http://applicationa.org/image.jpg
                  status:
                    type: string
                    example: Pending
    """
    applications = Application.query.all()
    return jsonify([application.to_dict() for application in applications]), 200

@app.route('/applications/<int:application_id>', methods=['GET'])
def get_application(application_id):
    """
    Get details of a specific application
    ---
    parameters:
      - name: application_id
        in: path
        description: ID of the application to retrieve
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Details of the application
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Application A
                description:
                  type: string
                  example: Description of Application A
                website:
                  type: string
                  example: http://applicationa.org
                image_url:
                  type: string
                  example: http://applicationa.org/image.jpg
                status:
                  type: string
                  example: Pending
      404:
        description: Application not found
    """
    application = Application.query.get_or_404(application_id)
    return jsonify(application.to_dict()), 200

@app.route('/applications', methods=['POST'])
def create_application():
    """
    Create a new application
    ---
    parameters:
      - name: body
        in: body
        description: Application information
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Application B
            description:
              type: string
              example: Description of Application B
            website:
              type: string
              example: http://applicationb.org
            image_url:
              type: string
              example: http://applicationb.org/image.jpg
            status:
              type: string
              example: Pending
    responses:
      201:
        description: Application created successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Application B
                description:
                  type: string
                  example: Description of Application B
                website:
                  type: string
                  example: http://applicationb.org
                image_url:
                  type: string
                  example: http://applicationb.org/image.jpg
                status:
                  type: string
                  example: Pending
    """
    data = request.get_json()
    new_application = Application(
        name=data['name'],
        description=data['description'],
        website=data.get('website'),
        image_url=data.get('image_url'),
        status='Pending'
    )
    db.session.add(new_application)
    db.session.commit()
    return jsonify(new_application.to_dict()), 201

@app.route('/applications/<int:application_id>', methods=['PATCH'])
def update_application(application_id):
    """
    Update an application
    ---
    parameters:
      - name: application_id
        in: path
        description: ID of the application to update
        required: true
        schema:
          type: integer
      - name: body
        in: body
        description: Updated application information
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: Application B Updated
            description:
              type: string
              example: Updated description of Application B
            website:
              type: string
              example: http://applicationb-updated.org
            status:
              type: string
              example: Approved
            image_url:
              type: string
              example: http://applicationb-updated.org/image.jpg
    responses:
      200:
        description: Application updated successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                name:
                  type: string
                  example: Application B Updated
                description:
                  type: string
                  example: Updated description of Application B
                website:
                  type: string
                  example: http://applicationb-updated.org
                image_url:
                  type: string
                  example: http://applicationb-updated.org/image.jpg
                status:
                  type: string
                  example: Approved
      404:
        description: Application not found
    """
    application = Application.query.get_or_404(application_id)
    data = request.get_json()
    if 'name' in data:
        application.name = data['name']
    if 'description' in data:
        application.description = data['description']
    if 'website' in data:
        application.website = data['website']
    if 'status' in data:
        application.status = data['status']
    if 'image_url' in data:
        application.image_url = data['image_url']
    db.session.commit()
    return jsonify(application.to_dict()), 200

@app.route('/applications/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    """
    Delete an application
    ---
    parameters:
      - name: application_id
        in: path
        description: ID of the application to delete
        required: true
        schema:
          type: integer
    responses:
      204:
        description: Application deleted successfully
      404:
        descriptionn: Application not found
    """
    application = Application.query.get(application_id)
    if not application:
        return jsonify({'msg': 'Application not found'}), 404
    db.session.delete(application)
    db.session.commit()
    return '', 204

# Admin login route
@app.route('/admin/login', methods=['POST'])
def admin_login():
    """
    Admin login
    ---
    tags:
      - Admin
    parameters:
      - in: body
        name: body
        description: Admin login information
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: admin@example.com
            password:
              type: string
              example: adminpassword123
    responses:
      200:
        description: Successful login
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: 'Login successful'
      401:
        description: Invalid email or password
        content:
          application/json:
            schema:
              type: object
              properties:
                msg:
                  type: string
                  example: 'Invalid email or password'
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Search for the admin by email
    admin = Admin.query.filter_by(email=email).first()

    if admin and bcrypt.checkpw(password.encode('utf-8'), admin.password.encode('utf-8')):
        return jsonify({'message': 'Login successful'}), 200

    return jsonify({'msg': 'Invalid email or password'}), 401

# Admin register route
@app.route('/admin/register', methods=['POST'])
def admin_register():
    """
    Admin registration
    ---
    tags:
      - Admin
    parameters:
      - in: body
        name: body
        description: Admin registration information
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: adminuser
            email:
              type: string
              example: admin@example.com
            password:
              type: string
              example: adminpassword123
    responses:
      201:
        description: Admin successfully registered
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: 'Admin successfully registered'
      400:
        description: Email already exists
        content:
          application/json:
            schema:
              type: object
              properties:
                msg:
                  type: string
                  example: 'Email already exists'
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # Check if the email is already registered
    if Admin.query.filter_by(email=email).first():
        return jsonify({'msg': 'Email already exists'}), 400

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Create a new admin instance
    new_admin = Admin(username=username, email=email, password=hashed_password)

    # Add the new admin to the database
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({'message': 'Admin successfully registered'}), 201

# Admin logout route
@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    """
    Logout an admin
    ---
    responses:
      200:
        description: Logout successful
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: 'Logout successful'
    """
    return jsonify({'message': 'Logout successful'}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)