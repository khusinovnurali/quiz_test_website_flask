from app import create_app
# Import the main models so SQLAlchemy can configure relationships in any order
from app.models.user import User
from app.models.score import Score
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.chapter import Chapter
from app.models.subject import Subject

app = create_app()
with app.app_context():
    qs = Quiz.query.all()
    if not qs:
        print('No quizzes found')
    else:
        for q in qs:
            print(f'id={q.id}  name="{q.name}"')
