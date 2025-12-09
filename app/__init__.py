from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.settings.Config')
    
    db.init_app(app)
    
    migrate = Migrate(app, db)

    login_manager.init_app(app)

    # Import blueprints
    from app.controllers.admin_controller import admin_bp
    from app.controllers.auth_controller import auth_bp
    from app.controllers.users_controller import users_bp
    from app.controllers.comments_controller import comments_bp

    # Register blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(comments_bp)

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    @app.route('/')
    def home():
        from app.models.comment import Comment
        # Get app comments (not quiz-specific)
        app_comments = Comment.query.filter_by(comment_type='app').order_by(Comment.created_at.desc()).limit(20).all()
        return render_template('home.html', comments=app_comments)

    # Ensure models are imported so SQLAlchemy knows table metadata
    with app.app_context():
        try:
            # Explicit imports register models with SQLAlchemy metadata
            from .models.user import User
            from .models.quiz import Quiz
            from .models.question import Question
            from .models.chapter import Chapter
            from .models.subject import Subject
            from .models.score import Score
            from .models.answer import Answer
            from .models.certificate import Certificate
            from .models.comment import Comment
        except Exception as e:
            # If imports fail, log but continue; errors will surface elsewhere
            import logging
            logging.warning(f"Failed to import some models: {e}")

        # Create tables automatically - always ensure tables exist
        try:
            db.create_all()
            import logging
            logging.info("Database tables initialized")
        except Exception as e:
            import logging
            logging.error(f"Failed to create database tables: {e}")
            # Don't raise - let the app start, but log the error

    return app

