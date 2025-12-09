import os
import sys
import logging
from flask import render_template

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from app import create_app, db
    from config.commands import register_commands
    from config.auto_init import auto_initialize
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

def init_database(app):
    """Initialize database tables"""
    with app.app_context():
        try:
            # Import all models here to ensure SQLAlchemy knows about them
            from app.models.user import User
            from app.models.quiz import Quiz
            from app.models.question import Question
            from app.models.chapter import Chapter
            from app.models.subject import Subject
            from app.models.score import Score
            from app.models.answer import Answer
            from app.models.certificate import Certificate
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise

def create_application():
    """Application factory with error handling"""
    try:
        app = create_app()
        register_commands(app)
        
        # Always initialize DB to ensure tables exist
        init_database(app)
        
        # Auto-initialize admin, test user, and quiz
        with app.app_context():
            auto_initialize()
        
        # Register error handlers
        app.register_error_handler(404, not_found_error)
        app.register_error_handler(500, internal_error)
        
        return app
    except Exception as e:
        logger.error(f"Failed to create application: {e}")
        sys.exit(1)

def not_found_error(error):
    return render_template('errors/404.html'), 404

def internal_error(error):
    logger.exception("Internal server error occurred")
    return render_template('errors/500.html'), 500

app = create_application()

if __name__ == '__main__':
    # Development server configuration
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host=host, port=port)
