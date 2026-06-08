"""initial migration

Revision ID: 501ece629d80
Revises: 
Create Date: 2025-11-21 15:06:28.981531

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '501ece629d80'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'produtos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('quantidade', sa.Integer(), nullable=False),
        sa.Column('preco_unitario', sa.Numeric(10, 2), nullable=True),
        sa.Column('observacao', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'historico',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('acao', sa.String(length=100), nullable=False),
        sa.Column('produto_nome', sa.String(length=100), nullable=False),
        sa.Column('quantidade', sa.Integer(), nullable=True),
        sa.Column('valor', sa.Numeric(10, 2), nullable=True),
        sa.Column('data_hora', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('historico')
    op.drop_table('produtos')