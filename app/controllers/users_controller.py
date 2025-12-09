from flask import Blueprint, render_template, redirect, flash, url_for, request, session
from app import db
from flask_login import current_user, login_required
from random import shuffle
import os, csv, time
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from app.forms import UserDetailsForm, ChangePasswordForm
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.score import Score
from app.models.answer import Answer
from app.models.certificate import Certificate
from app.models.subject import Subject
from app.models.user import User

users_bp = Blueprint('users', __name__)

@users_bp.route("/dashboard")
@login_required
def dashboard():
    scores = Score.query.filter_by(user_id=current_user.id).all()
    total_attempted_quizzes = len(scores)

    average_score = sum([s.total_scored for s in scores]) / total_attempted_quizzes if total_attempted_quizzes > 0 else 0

    return render_template("user/dashboard.html",
                           scores=scores,
                           total_attempted_quizzes=total_attempted_quizzes,
                           average_score=average_score)

@users_bp.route("/attempt_quiz/<int:quiz_id>", methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        # Get mapping from session
        session_key = f'quiz_mapping_{quiz_id}'
        question_option_mapping = session.get(session_key, {})
        
        # Clear the session mapping after use
        if session_key in session:
            del session[session_key]
        
        total_awarded = 0.0
        total_possible = 0.0

        # create score placeholder
        user_score = Score(
            total_scored=0.0,
            quiz_id=quiz_id,
            user_id=current_user.id
        )
        db.session.add(user_score)
        db.session.flush()  # get id

        # Get all questions for this quiz
        questions = quiz.questions
        
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            sel = int(user_answer) if user_answer and user_answer.isdigit() else None
            
            # Get mapping for this question
            mapping = question_option_mapping.get(str(question.id), {})
            correct_shuffled = mapping.get('correct_shuffled')
            is_correct = (sel == correct_shuffled) if (sel and correct_shuffled) else False
            points = float(question.points or 0.0)
            total_possible += points
            awarded = points if is_correct else 0.0
            total_awarded += awarded

            # Store the original option number that was selected
            original_selected = None
            if sel and mapping.get('shuffled_options'):
                shuffled_opts = mapping['shuffled_options']
                # shuffled_opts is list of lists: [[text, orig_num], ...]
                if 1 <= sel <= len(shuffled_opts):
                    original_selected = shuffled_opts[sel - 1][1]  # Get original option number

            ans = Answer(
                score_id=user_score.id,
                question_id=question.id,
                selected_option=original_selected,
                is_correct=is_correct,
                points_awarded=awarded
            )
            db.session.add(ans)

        # finalize score
        user_score.total_scored = total_awarded
        db.session.commit()

        percent = (total_awarded / total_possible * 100) if total_possible > 0 else 0
        flash(f'Quiz completed! Your score: {total_awarded:.2f} / {total_possible:.2f} ({percent:.2f}%)', category="success")

        # generate PDF certificate for high scorers
        try:
            if percent >= 86:
                # Create certificates directory if it doesn't exist
                certs_dir = os.path.join(os.getcwd(), 'static', 'certificates')
                os.makedirs(certs_dir, exist_ok=True)
                
                # Generate unique filename with timestamp
                timestamp = int(time.time())
                filename = f"certificate_{current_user.id}_{quiz_id}_{timestamp}.pdf"
                relative_path = os.path.join('static', 'certificates', filename).replace('\\', '/')
                filepath = os.path.join(os.getcwd(), relative_path)
                
                # Get subject and chapter info
                subject_name = quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else "General"
                chapter_name = quiz.chapter.name if quiz.chapter else "General"
                
                # Create PDF certificate
                doc = SimpleDocTemplate(filepath, pagesize=A4)
                story = []
                
                # Define styles
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#6366f1'),
                    spaceAfter=30,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Bold'
                )
                heading_style = ParagraphStyle(
                    'CustomHeading',
                    parent=styles['Heading2'],
                    fontSize=18,
                    textColor=colors.HexColor('#1e293b'),
                    spaceAfter=20,
                    alignment=TA_CENTER,
                    fontName='Helvetica-Bold'
                )
                normal_style = ParagraphStyle(
                    'CustomNormal',
                    parent=styles['Normal'],
                    fontSize=12,
                    textColor=colors.HexColor('#64748b'),
                    spaceAfter=15,
                    alignment=TA_CENTER,
                    fontName='Helvetica'
                )
                info_style = ParagraphStyle(
                    'CustomInfo',
                    parent=styles['Normal'],
                    fontSize=14,
                    textColor=colors.HexColor('#1e293b'),
                    spaceAfter=10,
                    alignment=TA_LEFT,
                    fontName='Helvetica'
                )
                
                # Add content
                story.append(Spacer(1, 1.5*inch))
                story.append(Paragraph("CERTIFICATE OF ACHIEVEMENT", title_style))
                story.append(Spacer(1, 0.5*inch))
                story.append(Paragraph("This is to certify that", normal_style))
                story.append(Spacer(1, 0.3*inch))
                story.append(Paragraph(current_user.fullname or current_user.username, heading_style))
                story.append(Spacer(1, 0.3*inch))
                story.append(Paragraph("has successfully completed the quiz", normal_style))
                story.append(Spacer(1, 0.5*inch))
                
                # Add quiz information table
                data = [
                    ['Subject:', subject_name],
                    ['Chapter:', chapter_name],
                    ['Quiz:', quiz.name],
                    ['Score:', f"{total_awarded:.2f} / {total_possible:.2f}"],
                    ['Percentage:', f"{percent:.2f}%"],
                    ['Date:', time.strftime('%Y-%m-%d %H:%M:%S')]
                ]
                
                table = Table(data, colWidths=[2*inch, 4*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e293b')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                    ('TOPPADDING', (0, 0), (-1, -1), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ]))
                
                story.append(table)
                story.append(Spacer(1, 0.5*inch))
                story.append(Paragraph("Congratulations on your achievement!", normal_style))
                
                # Build PDF
                doc.build(story)
                
                # Create certificate record
                cert = Certificate(
                    user_id=current_user.id,
                    quiz_id=quiz_id,
                    file_path=relative_path
                )
                db.session.add(cert)
                db.session.commit()
                
                flash('Certificate generated successfully!', 'success')
        except Exception as e:
            # Log the error but don't block quiz flow
            print('Certificate generation failed:', str(e))
            import traceback
            traceback.print_exc()
            flash('Certificate generation failed. Please contact administrator.', 'error')

        return redirect(url_for("users.quiz_results", quiz_id=quiz_id))
    
    # GET request - prepare quiz with shuffled options
    questions = quiz.questions.copy()
    shuffle(questions)
    
    # Create a list of questions with randomized options
    questions_with_options = []
    # Store mapping for POST processing in session
    question_option_mapping = {}
    
    for q in questions:
        options = [(q.option1, 1), (q.option2, 2), (q.option3, 3), (q.option4, 4)]
        shuffle(options)
        questions_with_options.append((q, options))
        # Create mapping: shuffled_position -> original_option_number
        # And find where the correct option ended up after shuffling
        shuffled_correct = None
        for idx, (opt_text, orig_num) in enumerate(options, start=1):
            if orig_num == q.correct_option:
                shuffled_correct = idx
                break
        # Store as string key for JSON serialization
        # Convert tuples to lists for JSON serialization
        shuffled_options_list = [[opt_text, orig_num] for opt_text, orig_num in options]
        question_option_mapping[str(q.id)] = {
            'shuffled_options': shuffled_options_list,  # List of [text, orig_num]
            'correct_shuffled': shuffled_correct
        }
    
    # Store mapping in session for POST request
    session_key = f'quiz_mapping_{quiz_id}'
    session[session_key] = question_option_mapping
    
    return render_template("user/attempt_quiz.html", quiz=quiz, questions_with_options=questions_with_options)

@users_bp.route("/quiz_results/<int:quiz_id>")
@login_required
def quiz_results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    answers = []
    total_possible = 0.0
    if score:
        answers = score.answers
        for a in answers:
            if a.question and a.question.points:
                total_possible += float(a.question.points)
    percent = (score.total_scored / total_possible * 100) if score and total_possible > 0 else 0

    certificate = Certificate.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).order_by(Certificate.created_at.desc()).first()
    
    # Get quiz comments
    quiz_comments = Comment.query.filter_by(comment_type='quiz', quiz_id=quiz_id).order_by(Comment.created_at.desc()).limit(20).all()

    return render_template("user/quiz_results.html", quiz=quiz, score=score, answers=answers, total_possible=total_possible, percent=percent, certificate=certificate, comments=quiz_comments)

@users_bp.route("/leaderboard")
@login_required
def leaderboard():
    # filters
    subject_id = request.args.get('subject_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    min_score = request.args.get('min_score')

    # Convert dates to datetime with time boundaries
    from datetime import datetime, time
    try:
        start_datetime = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(), time.min) if start_date else None
        end_datetime = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(), time.max) if end_date else None
    except (ValueError, TypeError):
        start_datetime = None
        end_datetime = None

    try:
        min_score_float = float(min_score) if min_score else None
    except ValueError:
        min_score_float = None

    users = User.get_all_users()
    leaderboard_data = []

    subject_name = Subject.query.get(subject_id).name if subject_id else None

    for user in users:
        # base query with eager loading
        q = Score.query.filter_by(user_id=user.id)
        if subject_id:
            q = q.join(Quiz).join(Chapter).filter(Chapter.subject_id == int(subject_id))
        if start_datetime:
            q = q.filter(Score.timestamp >= start_datetime)
        if end_datetime:
            q = q.filter(Score.timestamp <= end_datetime)
            
        scores = q.all()
        total_score = sum([s.total_scored for s in scores])
        avg_score = total_score / len(scores) if scores else 0
        
        # Apply filters
        if subject_id and total_score == 0:
            continue
        if min_score_float and total_score < min_score_float:
            continue
            
        leaderboard_data.append({
            "user_fullname": user.fullname,
            "total_score": total_score,
            "avg_score": avg_score,
            "quiz_count": len(scores),
            "user": user
        })
    
    leaderboard_data.sort(key=lambda x: (x['total_score'], x['avg_score']), reverse=True)
    user_fullnames = [x['user_fullname'] for x in leaderboard_data]
    user_total_scores = [x['total_score'] for x in leaderboard_data]
    
    # Get all subjects for filter dropdown
    subjects = Subject.query.order_by(Subject.name).all()
    
    return render_template("user/leaderboard.html",
                           leaderboard_data=leaderboard_data,
                           user_fullnames=user_fullnames,
                           user_total_scores=user_total_scores,
                           subjects=subjects,
                           subject_name=subject_name,
                           filters={
                               'subject_id': subject_id,
                               'start_date': start_date,
                               'end_date': end_date,
                               'min_score': min_score_float
                           },
                           has_filters=bool(subject_id or start_date or end_date or min_score))

@users_bp.route("/select-quiz", methods=['GET'])
@login_required
def select_quiz():
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    
    subject_id = request.args.get('subject_id')
    chapter_id = request.args.get('chapter_id')
    
    # Base query with eager loading
    quiz_query = Quiz.query.join(Chapter).join(Subject)
    
    if subject_id:
        quiz_query = quiz_query.filter(Chapter.subject_id == subject_id)
    if chapter_id:
        quiz_query = quiz_query.filter(Quiz.chapter_id == chapter_id)
    
    quizzes = quiz_query.order_by(Subject.name, Chapter.name, Quiz.name).all()

    return render_template("user/select-quiz.html",
                           subjects=subjects,
                           chapters=chapters,
                           quizzes=quizzes,
                           subject_id=subject_id,
                           chapter_id=chapter_id)

@users_bp.route("/update-profile", methods=['GET', 'POST'])
@login_required
def update_profile():
    user = current_user
    form = UserDetailsForm(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.fullname = form.fullname.data
        user.qualification = form.qualification.data
        user.dob = form.dob.data
        user.avatar = form.avatar.data

        db.session.commit()
        flash("User details updated successfully!", category="success")
        return redirect(url_for("users.dashboard"))

    certificates = user.certificates if hasattr(user, 'certificates') else []
    return render_template("user/update-profile.html",
                           form=form,
                           user=user,
                           certificates=certificates)

@users_bp.route("/change-password", methods=['GET', 'POST'])
@login_required
def change_password():
    user = current_user
    form = ChangePasswordForm(obj=user)

    if form.validate_on_submit():
        user.set_password(form.password.data)

        db.session.commit()
        flash("Password has been changed successfully!", category="success")
        return redirect(url_for("users.dashboard"))

    return render_template("user/change-password.html",
                           form=form,
                           user=user)

@users_bp.route("/search")
@login_required
def search_users():
    query = request.args.get('q', '')
    if query:
        users = User.query.filter(
            (User.fullname.ilike(f'%{query}%')) |
            (User.username.ilike(f'%{query}%')) |
            (User.qualification.ilike(f'%{query}%'))
        ).all()
    else:
        users = []
    return render_template("user/search_results.html", users=users, query=query)

@users_bp.route("/profile/<int:user_id>")
@login_required
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    scores = Score.query.filter_by(user_id=user.id).join(Score.quiz).order_by(Score.timestamp.desc()).limit(5).all()
    certificates = Certificate.query.filter_by(user_id=user.id).join(Certificate.quiz).order_by(Certificate.created_at.desc()).all()
    return render_template("user/view_profile.html", user=user, scores=scores, certificates=certificates)