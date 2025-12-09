import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app, db

os.environ['SQLALCHEMY_DATABASE_URI']='sqlite:///:memory:'
app = create_app()
app.config['TESTING']=True
app.config['WTF_CSRF_ENABLED']=False
client = app.test_client()
with app.app_context():
    db.create_all()
    rv = client.post('/auth/register', data={
        'username':'user2@example.com',
        'password':'password123',
        'confirm_password':'password123',
        'fullname':'User Two',
        'qualification':'Test',
        'dob':'1990-01-01',
        'avatar':'person-circle'
    }, follow_redirects=True)
    print('status', rv.status_code)
    print(rv.get_data(as_text=True)[:1000])
    from app.models.user import User
    u = User.query.filter_by(username='user2@example.com').first()
    print('user found:', u)
