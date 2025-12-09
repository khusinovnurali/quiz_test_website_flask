"""add points column to question table

Revision ID: add_points_column
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_points_column'
down_revision = None  # replace with your last migration id

def upgrade():
    # Add points column with default value 1
    op.add_column('question',
        sa.Column('points', sa.Integer(), 
        nullable=False, 
        server_default='1')
    )

def downgrade():
    op.drop_column('question', 'points')
