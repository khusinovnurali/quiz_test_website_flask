import os
from flask import current_app
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String)
    dob = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    avatar = db.Column(db.String(200), default='person-circle')  # Bootstrap icon name

    scores = db.relationship('Score', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @classmethod
    def get_all_users(cls):
        admin_username = None
        try:
            if current_app and current_app.config:
                admin_username = current_app.config.get('ADMIN_USERNAME')
        except RuntimeError:
            # current_app might not be available outside app context
            pass

        if not admin_username:
            admin_username = os.getenv('ADMIN_USERNAME', 'admin@quiz.com')

        return cls.query.filter(cls.is_admin.is_(False), cls.username != admin_username).all()
