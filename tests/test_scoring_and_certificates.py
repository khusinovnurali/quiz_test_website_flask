import os
import tempfile
import time
from app import create_app, db
from app.models.user import User
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from app.models.answer import Answer
from app.models.certificate import Certificate


def setup_app():
    # ensure the app uses an in-memory sqlite DB before creating app
    os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    # override again to be safe
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    return app


def test_scoring_and_certificate_generation(tmp_path):
    app = setup_app()
    client = app.test_client()

    with app.app_context():
        db.create_all()

        # create admin and user
        user = User(username='user@example.com', fullname='Test User')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # create subject, chapter, quiz
        subject = Subject(name='Math')
        db.session.add(subject)
        db.session.commit()

        chapter = Chapter(name='Algebra', subject_id=subject.id)
        db.session.add(chapter)
        db.session.commit()

        quiz = Quiz(name='Quiz1', chapter_id=chapter.id, time_duration=0)
        db.session.add(quiz)
        db.session.commit()

        # add questions: total possible 10
        q1 = Question(question_statement='q1', option1='a', option2='b', option3='c', option4='d', correct_option=1, quiz_id=quiz.id, points=3.0)
        q2 = Question(question_statement='q2', option1='a', option2='b', option3='c', option4='d', correct_option=2, quiz_id=quiz.id, points=7.0)
        db.session.add_all([q1, q2])
        db.session.commit()

        # login user using test client by manipulating session
        client.post('/register', data={
            'username':'user2@example.com',
            'password':'password123',
            'confirm_password':'password123',
            'fullname':'User Two',
            'qualification':'Test',
            'dob':'1990-01-01',
            'avatar':'person-circle'
        })
        # find created user2
        test_user = User.query.filter_by(username='user2@example.com').first()
        assert test_user is not None

        # simulate attempt_quiz post as test_user by forcing login via login_user endpoint
        # perform login
        rv = client.post('/login', data={'username':'user2@example.com','password':'password123'}, follow_redirects=True)
        assert b'Login successful' in rv.get_data() or b'Admin logged in' in rv.get_data()

        # submit answers: get quiz page first
        get = client.get(f'/attempt_quiz/{quiz.id}')
        assert get.status_code == 200

        # post answers: correct both -> total_awarded = 10 -> percent 100
        post_data = {
            f'question_{q1.id}': '1',
            f'question_{q2.id}': '2'
        }
        rv2 = client.post(f'/attempt_quiz/{quiz.id}', data=post_data, follow_redirects=True)
        assert b'Quiz completed' in rv2.get_data()

        # verify Score and Answer created
        sc = Score.query.filter_by(user_id=test_user.id, quiz_id=quiz.id).first()
        assert sc is not None
        assert abs(sc.total_scored - 10.0) < 1e-6

        answers = Answer.query.filter_by(score_id=sc.id).all()
        assert len(answers) == 2
        for a in answers:
            assert a.is_correct is True
            assert a.points_awarded in (3.0, 7.0)

        # certificate should be created for >=86%
        cert = Certificate.query.filter_by(user_id=test_user.id, quiz_id=quiz.id).first()
        assert cert is not None
        # file should exist
        file_path = os.path.join(os.getcwd(), cert.file_path)
        assert os.path.exists(file_path)

        # cleanup created certificate file
        try:
            os.remove(file_path)
        except Exception:
            pass

        db.drop_all()


def test_leaderboard_filter_by_subject():
    app = setup_app()
    client = app.test_client()

    with app.app_context():
        db.create_all()
        # users
        u1 = User(username='u1@example.com', fullname='U One')
        u1.set_password('pass')
        u2 = User(username='u2@example.com', fullname='U Two')
        u2.set_password('pass')
        db.session.add_all([u1,u2])
        db.session.commit()

        # subjects, chapters, quizzes
        s1 = Subject(name='S1')
        s2 = Subject(name='S2')
        db.session.add_all([s1,s2]); db.session.commit()
        c1 = Chapter(name='C1', subject_id=s1.id); c2 = Chapter(name='C2', subject_id=s2.id)
        db.session.add_all([c1,c2]); db.session.commit()
        qz1 = Quiz(name='Q1', chapter_id=c1.id); qz2 = Quiz(name='Q2', chapter_id=c2.id)
        db.session.add_all([qz1,qz2]); db.session.commit()

        # scores: u1 -> qz1 score 5, u2 -> qz2 score 7
        sc1 = Score(total_scored=5.0, quiz_id=qz1.id, user_id=u1.id)
        sc2 = Score(total_scored=7.0, quiz_id=qz2.id, user_id=u2.id)
        db.session.add_all([sc1,sc2]); db.session.commit()

        # login as one user to access leaderboard
        client.post('/register', data={'username':'viewer@example.com','password':'password123','confirm_password':'password123','fullname':'Viewer','qualification':'','dob':'1990-01-01','avatar':'person-circle'})
        client.post('/login', data={'username':'viewer@example.com','password':'password123'})

        # filter leaderboard by subject s1 -> should include u1 but not u2
        possible_paths = [f'/users/leaderboard?subject_id={s1.id}', f'/leaderboard?subject_id={s1.id}', f'/users/leaderboard/?subject_id={s1.id}']
        rv = None
        for p in possible_paths:
            rv = client.get(p)
            if rv.status_code == 200:
                break
        assert rv is not None and rv.status_code == 200
        html = rv.get_data(as_text=True)
        assert 'U One' in html
        assert 'U Two' not in html

        db.drop_all()