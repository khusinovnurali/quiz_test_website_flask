from alembic import op
import sqlalchemy as sa

revision = 'add_points_to_questions'
down_revision = None  # Update this with your last migration ID

def upgrade():
    op.add_column('question', sa.Column('points', sa.Integer(), nullable=False, server_default='1'))

def downgrade():
    op.drop_column('question', 'points')
