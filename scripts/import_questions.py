"""
Simple questions importer script for this app.

Format (plain text):
Each question block separated by a blank line.
Lines within a block:
1) question statement
2) option 1
3) option 2
4) option 3
5) option 4
6) correct option number (1-4)

Example block:
What is 2+2?
1
2
3
4
4

Usage:
& .venv\Scripts\python.exe scripts\import_questions.py <path-to-file> <quiz_id>

This script will create questions for the given quiz id.
"""

import sys
from app import create_app, db
# Import all related models so SQLAlchemy can configure relationships
from app.models.user import User
from app.models.score import Score
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.chapter import Chapter
from app.models.subject import Subject


def parse_blocks(lines):
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
    # Accept blocks with at least 6 lines; extra lines will be ignored
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


def main():
    if len(sys.argv) != 3:
        print('Usage: import_questions.py <path-to-txt> <quiz_id>')
        sys.exit(2)
    path = sys.argv[1]
    quiz_id = None
    try:
        quiz_id = int(sys.argv[2])
    except ValueError:
        print('quiz_id must be an integer')
        sys.exit(2)

    app = create_app()
    with app.app_context():
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            print(f'Quiz with id {quiz_id} not found')
            sys.exit(1)

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        blocks = parse_blocks(lines)
        print(f'Found {len(blocks)} question blocks in file')

        created = 0
        for i, b in enumerate(blocks, start=1):
            try:
                qdata = parse_block_to_question(b)
            except Exception as e:
                print(f'Skipping block {i}: parse error: {e}')
                continue
            question = Question(
                question_statement=qdata['question_statement'],
                option1=qdata['option1'],
                option2=qdata['option2'],
                option3=qdata['option3'],
                option4=qdata['option4'],
                correct_option=qdata['correct_option'],
                quiz_id=quiz_id
            )
            db.session.add(question)
            created += 1
        db.session.commit()
        print(f'Imported {created} questions into quiz id {quiz_id}')


if __name__ == '__main__':
    main()
