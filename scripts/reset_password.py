"""
Script to reset user password
Usage: python scripts/reset_password.py <username> <new_password>
"""
import sys
import os
from app import create_app, db
from app.models.user import User

def reset_password(username, new_password):
    """Reset user password"""
    app = create_app()
    with app.app_context():
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                print(f"✗ User '{username}' not found!")
                return False
            
            if len(new_password) < 8:
                print(f"✗ Password must be at least 8 characters!")
                return False
            
            user.set_password(new_password)
            db.session.commit()
            print(f"✓ Password reset successfully for user: {username}")
            print(f"  New password: {new_password}")
            return True
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error resetting password: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python scripts/reset_password.py <username> <new_password>")
        print("Example: python scripts/reset_password.py admin@quiz.com admin1234")
        sys.exit(1)
    
    username = sys.argv[1]
    new_password = sys.argv[2]
    
    if reset_password(username, new_password):
        sys.exit(0)
    else:
        sys.exit(1)

