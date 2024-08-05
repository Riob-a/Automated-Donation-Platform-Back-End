from app import app, db
from models import User, Charity, Donation, Beneficiary
import bcrypt

# Sample data
users = [
    {'username': 'john_doe', 'email': 'john@example.com', 'password': 'password123'},
    {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'securepassword'},
    {'username': 'derrick_rioba', 'email':'d@example.com', 'password': 'test1'}
]

charities = [
    {
        'name': 'Save the Girls',
        'description': 'Providing sanitary supplies to school girls in need.',
        'website': 'http://savethegirls.org',
        'approved': True,
        'image_url': 'http://example.com/images/savethegirls.jpg'
    },
    {
        'name': 'Education for All',
        'description': 'Supporting educational initiatives for underprivileged girls.',
        'website': 'http://educationforall.org',
        'approved': True,
        'image_url': 'http://example.com/images/educationforall.jpg'
    }
]

donations = [
    {'amount': 100.0, 'anonymous': False, 'user_id': 1, 'charity_id': 1},
    {'amount': 50.0, 'anonymous': True, 'user_id': 2, 'charity_id': 2}
]

beneficiaries = [
    {'name': 'Mary', 'story': 'A bright student with a passion for learning but lacks access to basic sanitary supplies.', 'charity_id': 1},
    {'name': 'Sophia', 'story': 'An aspiring engineer with dreams of a better future, supported by educational initiatives.', 'charity_id': 2}
]

def seed_db():
    with app.app_context():
        # Create tables
        db.create_all()

        # Seed users with hashed passwords
        for user_data in users:
            hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
            user = User(username=user_data['username'], email=user_data['email'], password=hashed_password.decode('utf-8'))
            db.session.add(user)

        # Seed charities
        for charity_data in charities:
            charity = Charity(
                name=charity_data['name'],
                description=charity_data['description'],
                website=charity_data['website'],
                approved=charity_data['approved'],
                image_url=charity_data['image_url']
            )
            db.session.add(charity)

        # Seed donations
        for donation_data in donations:
            donation = Donation(
                amount=donation_data['amount'],
                anonymous=donation_data['anonymous'],
                user_id=donation_data['user_id'],
                charity_id=donation_data['charity_id']
            )
            db.session.add(donation)

        # Seed beneficiaries
        for beneficiary_data in beneficiaries:
            beneficiary = Beneficiary(
                name=beneficiary_data['name'],
                story=beneficiary_data['story'],
                charity_id=beneficiary_data['charity_id']
            )
            db.session.add(beneficiary)

        # Commit the session
        db.session.commit()

if __name__ == '__main__':
    seed_db()
