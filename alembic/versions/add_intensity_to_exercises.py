from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '23749cfb7c53'
down_revision = None  # Set this to your previous migration's revision ID if you have one
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('exercises', sa.Column('intensity', sa.String(), nullable=True))
    op.execute("UPDATE exercises SET intensity = 'medium' WHERE intensity IS NULL")

def downgrade():
    op.drop_column('exercises', 'intensity') 