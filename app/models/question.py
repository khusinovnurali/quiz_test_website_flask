from app import db

class Question(db.Model):
    __tablename__ = 'question'
    
    id = db.Column(db.Integer, primary_key=True)
    question_statement = db.Column(db.String(500), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)
    correct_option = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, nullable=False, default=1)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    image_path = db.Column(db.String(200))