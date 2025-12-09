from app import db

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score_id = db.Column(db.Integer, db.ForeignKey('score.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_option = db.Column(db.Integer, nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    points_awarded = db.Column(db.Float, default=0.0)

    question = db.relationship('Question', backref='answers')
