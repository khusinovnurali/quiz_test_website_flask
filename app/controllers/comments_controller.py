from flask import Blueprint, render_template, redirect, flash, url_for, request, jsonify
from app import db
from flask_login import current_user, login_required
from app.models.comment import Comment
from app.models.quiz import Quiz
from datetime import datetime

comments_bp = Blueprint('comments', __name__)

@comments_bp.route("/comment/add", methods=['POST'])
@login_required
def add_comment():
    content = request.form.get('content', '').strip()
    comment_type = request.form.get('comment_type', 'app')  # 'app' or 'quiz'
    quiz_id = request.form.get('quiz_id', type=int)
    
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(request.referrer or url_for('home'))
    
    if comment_type == 'quiz' and not quiz_id:
        flash('Quiz ID is required for quiz comments', 'error')
        return redirect(request.referrer or url_for('home'))
    
    try:
        comment = Comment(
            user_id=current_user.id,
            content=content,
            comment_type=comment_type,
            quiz_id=quiz_id if comment_type == 'quiz' else None
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f'Error adding comment: {str(e)}')
        flash('Failed to add comment. Please try again.', 'error')
    
    return redirect(request.referrer or url_for('home'))

@comments_bp.route("/comment/<int:comment_id>/delete", methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    
    # Only allow users to delete their own comments or admins
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('You do not have permission to delete this comment', 'error')
        return redirect(request.referrer or url_for('home'))
    
    try:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        print(f'Error deleting comment: {str(e)}')
        flash('Failed to delete comment', 'error')
    
    return redirect(request.referrer or url_for('home'))

