"""
Manually add points column to existing question table
Run this script once to fix the database schema
"""
from app import create_app, db

app = create_app()

with app.app_context():
    # Execute raw SQL to add column
    try:
        # Check if column exists
        result = db.session.execute(db.text("PRAGMA table_info(question)"))
        columns = [row[1] for row in result]
        
        if 'points' not in columns:
            print("Adding 'points' column to question table...")
            db.session.execute(db.text(
                "ALTER TABLE question ADD COLUMN points FLOAT DEFAULT 1.0"
            ))
            db.session.commit()
            print("✓ Successfully added 'points' column with default value 1.0")
        else:
            print("✓ 'points' column already exists")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        db.session.rollback()