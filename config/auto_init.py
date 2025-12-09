"""
Automatic initialization module for creating admin, test user, and quiz from txt file
"""
import os
from datetime import datetime
from app import db
from app.models.user import User
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question


def parse_question_blocks(lines):
    """Parse question blocks from text file"""
    blocks = []
    current = []
    for ln in lines:
        s = ln.rstrip('\n')
        if s.strip() == "":
            if current:
                blocks.append(current)
                current = []
        else:
            current.append(s)
    if current:
        blocks.append(current)
    return blocks


def parse_block_to_question(block):
    """Parse a single question block to question data"""
    if len(block) < 6:
        raise ValueError('Block must have at least 6 non-empty lines')
    q_stmt = block[0].strip()
    opt1 = block[1].strip()
    opt2 = block[2].strip()
    opt3 = block[3].strip()
    opt4 = block[4].strip()
    correct_raw = block[5].strip()
    try:
        correct = int(correct_raw)
    except ValueError:
        raise ValueError('Correct option must be an integer 1-4')
    if correct < 1 or correct > 4:
        raise ValueError('Correct option must be 1-4')
    return {
        'question_statement': q_stmt,
        'option1': opt1,
        'option2': opt2,
        'option3': opt3,
        'option4': opt4,
        'correct_option': correct
    }


def create_admin():
    """Create admin user if not exists"""
    admin_username = os.getenv('ADMIN_USERNAME', 'admin@quiz.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    admin = User.query.filter_by(username=admin_username).first()
    if not admin:
        admin = User(
            username=admin_username,
            fullname="Quiz Master Admin",
            is_admin=True,
            avatar='person-circle'
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"✓ Admin created: {admin_username}")
        return admin
    else:
        print(f"✓ Admin already exists: {admin_username}")
        return admin


def create_test_user():
    """Create test user if not exists"""
    test_username = 'test@quiz.com'
    test_password = 'test1234'
    
    user = User.query.filter_by(username=test_username).first()
    if not user:
        user = User(
            username=test_username,
            fullname="Test User",
            qualification="Test",
            dob=datetime(1990, 1, 1).date(),
            is_admin=False,
            avatar='person-circle'
        )
        user.set_password(test_password)
        db.session.add(user)
        db.session.commit()
        print(f"✓ Test user created: {test_username} / {test_password} (8 characters)")
        return user
    else:
        print(f"✓ Test user already exists: {test_username}")
        return user


def create_test_quiz_from_file(txt_file_path='sample_questions.txt'):
    """Create test quiz with questions from txt file"""
    # Check if quiz already exists
    existing_quiz = Quiz.query.filter_by(name="Hujayra Testi").first()
    if existing_quiz and existing_quiz.questions.count() > 0:
        print(f"✓ Test quiz already exists with {existing_quiz.questions.count()} questions")
        return existing_quiz
    
    # Create or get Subject
    subject = Subject.query.filter_by(name="Biologiya").first()
    if not subject:
        subject = Subject(
            name="Biologiya",
            description="Biologiya fanidan testlar"
        )
        db.session.add(subject)
        db.session.commit()
        print("✓ Subject 'Biologiya' created")
    
    # Create or get Chapter
    chapter = Chapter.query.filter_by(name="Hujayra", subject_id=subject.id).first()
    if not chapter:
        chapter = Chapter(
            name="Hujayra",
            description="Hujayra tuzilishi va funksiyalari",
            subject_id=subject.id
        )
        db.session.add(chapter)
        db.session.commit()
        print("✓ Chapter 'Hujayra' created")
    
    # Create Quiz
    quiz = Quiz.query.filter_by(name="Hujayra Testi").first()
    if not quiz:
        quiz = Quiz(
            name="Hujayra Testi",
            date_of_quiz=datetime.now(),
            time_duration=30 * 60,  # 30 minutes
            chapter_id=chapter.id
        )
        db.session.add(quiz)
        db.session.flush()  # Get quiz.id
        print("✓ Quiz 'Hujayra Testi' created")
    
    # Import questions from txt file
    if os.path.exists(txt_file_path):
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        blocks = parse_question_blocks(lines)
        print(f"✓ Found {len(blocks)} question blocks in {txt_file_path}")
        
        created = 0
        for i, b in enumerate(blocks, start=1):
            try:
                qdata = parse_block_to_question(b)
                # Check if question already exists
                existing = Question.query.filter_by(
                    question_statement=qdata['question_statement'],
                    quiz_id=quiz.id
                ).first()
                if existing:
                    continue
                
                question = Question(
                    question_statement=qdata['question_statement'],
                    option1=qdata['option1'],
                    option2=qdata['option2'],
                    option3=qdata['option3'],
                    option4=qdata['option4'],
                    correct_option=qdata['correct_option'],
                    points=1,
                    quiz_id=quiz.id
                )
                db.session.add(question)
                created += 1
            except Exception as e:
                print(f"⚠ Skipping block {i}: {e}")
                continue
        
        db.session.commit()
        print(f"✓ Imported {created} questions into quiz")
    else:
        print(f"⚠ File {txt_file_path} not found, skipping question import")
    
    return quiz


def auto_initialize():
    """Main function to auto-initialize admin, test user, and quiz"""
    print("=" * 50)
    print("Auto-initializing database...")
    print("=" * 50)
    
    try:
        # Create admin
        create_admin()
        
        # Create test user
        create_test_user()
        
        # Create test quiz from txt file
        create_test_quiz_from_file()
        
        print("=" * 50)
        print("✓ Auto-initialization completed successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"✗ Error during auto-initialization: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

