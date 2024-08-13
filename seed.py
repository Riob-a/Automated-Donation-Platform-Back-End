from app import app, db
from models import User, Charity, Donation, Beneficiary, Application, Admin
import bcrypt

# Sample data
users = [
    {'username': 'john_doe', 'email': 'john@example.com', 'password': 'password123', 'is_admin': False},
    {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'securepassword', 'is_admin': False},
    {'username': 'derrick_rioba', 'email': 'd@example.com', 'password': 'test1', 'is_admin': True}
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
    {
        'name': 'Mary',
        'story': 'A bright student with a passion for learning but lacks access to basic sanitary supplies.',
        'image_url': 'http://example.com/images/mary.jpg',
        'charity_id': 1
    },
    {
        'name': 'Sophia',
        'story': 'An aspiring engineer with dreams of a better future, supported by educational initiatives.',
        'image_url': 'http://example.com/images/sophia.jpg',
        'charity_id': 2
    }
]

applications = [
    {
        'name': 'Health & Hygiene',
        'description': 'A program focused on promoting health and hygiene among school-aged girls.',
        'website': 'http://healthandhygiene.org',
        'image_url': 'http://example.com/images/healthandhygiene.jpg',
        'status': 'Pending'
    },
    {
        'name': 'Tech for Girls',
        'description': 'Providing technology resources and education to girls in rural areas.',
        'website': 'http://techforgirls.org',
        'image_url': 'http://example.com/images/techforgirls.jpg',
        'status': 'Pending'
    }
]

admins = [
    {'username': 'derrick_admin', 'email': 'admin@example.com', 'password': 'adminsecurepassword'},
    {'username': 'test', 'email': 'test@email.com', 'password': 'test1password'}
]

def seed_db():
    with app.app_context():
        # Create tables
        db.create_all()

        # Seed users with hashed passwords
        for user_data in users:
            hashed_password = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                password=hashed_password.decode('utf-8'),
                is_admin=user_data['is_admin']
            )
            db.session.add(user)

        # Seed admin users with hashed passwords
        for admin_data in admins:
            hashed_password = bcrypt.hashpw(admin_data['password'].encode('utf-8'), bcrypt.gensalt())
            admin = Admin(
                username=admin_data['username'],
                email=admin_data['email'],
                password=hashed_password.decode('utf-8')
            )
            db.session.add(admin)

        # Seed charities
        for charity_data in charities:
            charity = Charity(
                name=charity_data['name'],
                description=charity_data['description'],
                website=charity_data['website'],
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
                image_url=beneficiary_data['image_url'],
                charity_id=beneficiary_data['charity_id']
            )
            db.session.add(beneficiary)

        # Seed applications
        for application_data in applications:
            application = Application(
                name=application_data['name'],
                description=application_data['description'],
                website=application_data['website'],
                image_url=application_data['image_url'],
                status=application_data['status']
            )
            db.session.add(application)

        # Commit the session
        db.session.commit()

if __name__ == '__main__':
    seed_db()