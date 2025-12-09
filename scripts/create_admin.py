import os
import logging
from typing import Optional, Union
from datetime import datetime, date

from app import create_app, db

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def create_admin_user(
    username: str = 'admin@quiz.com',
    password: Optional[str] = None,
    init_db: bool = False,
    dob: Union[date, str] = None,
    fullname: str = 'Administrator',
    qualification: str = 'System Administrator',
    is_admin: bool = True
) -> bool:
    # Create app first, then import models inside the app context to avoid circular import
    app = create_app()
    with app.app_context():
        # Import models here so SQLAlchemy metadata is populated correctly
        try:
            from app.models.user import User
            from app.models.score import Score
            from app.models.quiz import Quiz
            from app.models.question import Question
            from app.models.chapter import Chapter
            from app.models.subject import Subject
        except Exception:
            logging.exception("Failed to import models (this may cause missing tables)")

        if init_db:
            try:
                db.create_all()
                logging.info("Database tables created (create_all).")
                return True
            except Exception:
                logging.exception("Failed to create DB tables")
                return False

        try:
            # Ensure tables exist before querying/inserting
            db.create_all()
        except Exception:
            logging.exception("Failed to ensure DB tables exist")
            return False

        try:
            admin = User.query.filter_by(username=username).first()
        except Exception:
            # If query fails, log and attempt to continue (likely metadata not registered)
            logging.exception("User query failed — metadata may be missing")
            return False

        if admin:
            logging.info("Admin user already exists: %s", username)
            return True

        pwd = password or os.environ.get('ADMIN_PASSWORD') or 'admin123'
        try:
            admin = User(
                username=username,  # type: str
                fullname=fullname,  # type: str
                qualification=qualification,  # type: str
                dob=dob or datetime.now().date(),  # type: date
                is_admin=is_admin,  # type: bool
                avatar='person-circle'  # default avatar
            )

            # Use setter if available, otherwise try to set attribute directly
            if hasattr(admin, 'set_password') and callable(getattr(admin, 'set_password')):
                admin.set_password(pwd)
            elif hasattr(admin, 'password'):
                admin.password = pwd
            else:
                logging.warning("No password setter or attribute found on User model; storing plain password not possible")

            db.session.add(admin)
            db.session.commit()
            logging.info("Admin user created successfully: %s", username)
            return True
        except Exception:
            db.session.rollback()
            logging.exception("Failed to create admin user")
            return False

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Create admin user for Quiz Master / init DB')
    parser.add_argument('--username', default='admin@quiz.com', help='Admin username/email')
    parser.add_argument('--password', default=None, help='Admin password (or set ADMIN_PASSWORD env)')
    parser.add_argument('--init-db', action='store_true', help='Only create database tables (db.create_all()) and exit')
    args = parser.parse_args()

    success = create_admin_user(username=args.username, password=args.password, init_db=args.init_db)
    if not success:
        exit(1)
