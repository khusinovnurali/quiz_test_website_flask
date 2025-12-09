"""
Add a single question to a quiz from the command line or interactively.

Usage examples (PowerShell):
& .venv\Scripts\python.exe scripts\add_question.py --quiz 2 --statement "What is 3+3?" --opt1 4 --opt2 5 --opt3 6 --opt4 7 --correct 3

Or interactively:
& .venv\Scripts\python.exe scripts\add_question.py --quiz 2

The script will validate correct option (1-4) and save the question.
"""

import argparse
import sys
from app import create_app, db
# import related models to ensure SQLAlchemy mappers initialize
from app.models.user import User
from app.models.score import Score
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.chapter import Chapter
from app.models.subject import Subject


def prompt_if_none(val, prompt_text):
    if val is not None:
        return val
    try:
        return input(prompt_text).strip()
    except KeyboardInterrupt:
        print('\nAborted')
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='Add a question to a quiz')
    parser.add_argument('--quiz', '-q', type=int, required=True, help='Quiz id to add the question to')
    parser.add_argument('--statement', '-s', type=str, help='Question statement')
    parser.add_argument('--opt1', type=str, help='Option 1')
    parser.add_argument('--opt2', type=str, help='Option 2')
    parser.add_argument('--opt3', type=str, help='Option 3')
    parser.add_argument('--opt4', type=str, help='Option 4')
    parser.add_argument('--correct', '-c', type=int, help='Correct option number (1-4)')

    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        quiz = Quiz.query.get(args.quiz)
        if not quiz:
            print(f'Quiz with id {args.quiz} was not found')
            sys.exit(1)

    # interactive prompts if missing
    statement = prompt_if_none(args.statement, 'Question statement: ')
    opt1 = prompt_if_none(args.opt1, 'Option 1: ')
    opt2 = prompt_if_none(args.opt2, 'Option 2: ')
    opt3 = prompt_if_none(args.opt3, 'Option 3: ')
    opt4 = prompt_if_none(args.opt4, 'Option 4: ')
    correct_raw = prompt_if_none(args.correct, 'Correct option number (1-4): ') if args.correct is None else str(args.correct)

    # validate
    try:
        correct = int(correct_raw)
    except ValueError:
        print('Correct option must be an integer 1-4')
        sys.exit(2)
    if correct < 1 or correct > 4:
        print('Correct option must be between 1 and 4')
        sys.exit(2)

    # create and save
    with app.app_context():
        question = Question(
            question_statement=statement,
            option1=opt1,
            option2=opt2,
            option3=opt3,
            option4=opt4,
            correct_option=correct,
            quiz_id=args.quiz
        )
        db.session.add(question)
        db.session.commit()
        print(f'Question added with id {question.id} to quiz id {args.quiz}')


if __name__ == '__main__':
    main()
