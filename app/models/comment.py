from app import db
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comment'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    comment_type = db.Column(db.String(20), nullable=False)  # 'app' or 'quiz'
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=True)  # None for app comments
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='comments')
    quiz = db.relationship('Quiz', backref='comments')

