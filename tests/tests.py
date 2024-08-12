import pytest
from datetime import datetime
from app import create_app, db
from app.models import User, Charity, UnapprovedCharity, Donation, Beneficiary, TokenBlacklist, Application, Admin

@pytest.fixture(scope='module')
def new_user():
    user = User(username='testuser', email='testuser@example.com', password='hashed_password')
    return user

@pytest.fixture(scope='module')
def new_charity():
    charity = Charity(name='Test Charity', description='A charity for testing purposes', website='http://testcharity.org')
    return charity

@pytest.fixture(scope='module')
def new_donation(new_user, new_charity):
    donation = Donation(amount=100.0, anonymous=False, donor=new_user, charity=new_charity)
    return donation

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()
    testing_client = flask_app.test_client()

    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()

@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table(s)
    db.create_all()

    # Insert user data
    user = User(username='admin', email='admin@example.com', password='adminpass', is_admin=True)
    charity = Charity(name='Charity One', description='A worthy cause', website='http://charityone.org')
    donation = Donation(amount=50.0, donor=user, charity=charity)
    db.session.add(user)
    db.session.add(charity)
    db.session.add(donation)

    # Commit the changes for the models
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()

### Tests ###

def test_new_user(new_user):
    assert new_user.username == 'testuser'
    assert new_user.email == 'testuser@example.com'
    assert new_user.password == 'hashed_password'
    assert new_user.is_admin is False

def test_new_charity(new_charity):
    assert new_charity.name == 'Test Charity'
    assert new_charity.description == 'A charity for testing purposes'
    assert new_charity.website == 'http://testcharity.org'
    assert new_charity.image_url is None

def test_new_donation(new_donation):
    assert new_donation.amount == 100.0
    assert new_donation.anonymous is False
    assert new_donation.donation_date <= datetime.utcnow()

def test_add_user_to_db(test_client, init_database, new_user):
    db.session.add(new_user)
    db.session.commit()
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.username == 'testuser'

def test_add_charity_to_db(test_client, init_database, new_charity):
    db.session.add(new_charity)
    db.session.commit()
    charity = Charity.query.filter_by(name='Test Charity').first()
    assert charity is not None
    assert charity.name == 'Test Charity'

def test_add_donation_to_db(test_client, init_database, new_donation):
    db.session.add(new_donation)
    db.session.commit()
    donation = Donation.query.filter_by(amount=100.0).first()
    assert donation is not None
    assert donation.amount == 100.0

def test_update_user(test_client, init_database):
    user = User.query.filter_by(username='testuser').first()
    user.email = 'newemail@example.com'
    db.session.commit()
    updated_user = User.query.filter_by(username='testuser').first()
    assert updated_user.email == 'newemail@example.com'

def test_delete_charity(test_client, init_database):
    charity = Charity.query.filter_by(name='Test Charity').first()
    db.session.delete(charity)
    db.session.commit()
    deleted_charity = Charity.query.filter_by(name='Test Charity').first()
    assert deleted_charity is None

### Tests for UnapprovedCharity ###

def test_new_unapproved_charity(new_unapproved_charity):
    assert new_unapproved_charity.name == 'Unapproved Charity'
    assert new_unapproved_charity.description == 'Pending approval'
    assert new_unapproved_charity.website == 'http://unapproved.org'
    assert new_unapproved_charity.date_submitted <= datetime.utcnow()

def test_add_unapproved_charity_to_db(test_client, init_database, new_unapproved_charity):
    db.session.add(new_unapproved_charity)
    db.session.commit()
    charity = UnapprovedCharity.query.filter_by(name='Unapproved Charity').first()
    assert charity is not None
    assert charity.name == 'Unapproved Charity'

### Tests for Beneficiary ###

def test_new_beneficiary(new_beneficiary):
    assert new_beneficiary.name == 'Test Beneficiary'
    assert new_beneficiary.story == 'A story for the beneficiary'
    assert new_beneficiary.charity is not None

def test_add_beneficiary_to_db(test_client, init_database, new_beneficiary):
    db.session.add(new_beneficiary)
    db.session.commit()
    beneficiary = Beneficiary.query.filter_by(name='Test Beneficiary').first()
    assert beneficiary is not None
    assert beneficiary.name == 'Test Beneficiary'

### Tests for TokenBlacklist ###

def test_new_token(new_token):
    assert new_token.token == 'sample_token_string'

def test_add_token_to_db(test_client, init_database, new_token):
    db.session.add(new_token)
    db.session.commit()
    token = TokenBlacklist.query.filter_by(token='sample_token_string').first()
    assert token is not None
    assert token.token == 'sample_token_string'

### Tests for Application ###

def test_new_application(new_application):
    assert new_application.name == 'Test Application'
    assert new_application.description == 'An application for testing'
    assert new_application.website == 'http://application.org'
    assert new_application.status == 'Pending'

def test_add_application_to_db(test_client, init_database, new_application):
    db.session.add(new_application)
    db.session.commit()
    application = Application.query.filter_by(name='Test Application').first()
    assert application is not None
    assert application.name == 'Test Application'

### Tests for Admin ###

def test_new_admin(new_admin):
    assert new_admin.username == 'adminuser'
    assert new_admin.email == 'adminuser@example.com'
    assert new_admin.password == 'adminpass'

def test_add_admin_to_db(test_client, init_database, new_admin):
    db.session.add(new_admin)
    db.session.commit()
    admin = Admin.query.filter_by(username='adminuser').first()
    assert admin is not None
    assert admin.username == 'adminuser'