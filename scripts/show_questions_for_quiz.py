from app import create_app
# Import related models to ensure SQLAlchemy mappers are configured
from app.models.user import User
from app.models.score import Score
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.chapter import Chapter
from app.models.subject import Subject

app = create_app()
with app.app_context():
    quiz_id = 2
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        print('Quiz not found')
    else:
        qs = quiz.questions
        print(f'Quiz id={quiz.id} name="{quiz.name}" has {len(qs)} questions:')
        for q in qs:
            print('-', (q.id, q.question_statement[:80].replace('\n',' ')))
