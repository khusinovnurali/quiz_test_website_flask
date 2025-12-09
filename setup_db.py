from app import create_app, db
from app.models.user import User
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score

app = create_app()

def setup_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables with new schema
        db.create_all()
        
        # Create admin user
        admin = User(
            username='admin@quiz.com',
            fullname='Administrator',
            is_admin=True,
            avatar='person-badge-fill'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()

if __name__ == '__main__':
    setup_database()