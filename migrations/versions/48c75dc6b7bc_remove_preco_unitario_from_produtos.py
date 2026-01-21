"""remove preco_unitario from produtos

Revision ID: 48c75dc6b7bc
Revises: a47633d4ad48
Create Date: 2025-12-20 21:15:13.864403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48c75dc6b7bc'
down_revision = 'a47633d4ad48'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('produtos', 'preco_unitario')


def downgrade():
    op.add_column(
        'produtos', 
        sa.Column('preco_unitario', sa.Numeric(10,), nullable=True)
    )