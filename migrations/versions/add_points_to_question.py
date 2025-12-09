"""add points to question

Revision ID: add_points_to_question
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_points_to_question'
down_revision = None  # Update this with your last migration's revision ID

def upgrade():
    op.add_column('question', 
        sa.Column('points', sa.Integer(), nullable=False, server_default='1')
    )

def downgrade():
    op.drop_column('question', 'points')
