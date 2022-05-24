"""Changes

Revision ID: dc7e6c5eda33
Revises: 83fdd5ce97a1
Create Date: 2022-05-23 08:58:25.687145

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'dc7e6c5eda33'
down_revision = '83fdd5ce97a1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'subscribes', ['id'])
    op.alter_column('transactions', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=True)
    op.create_unique_constraint(None, 'transactions', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'transactions', type_='unique')
    op.alter_column('transactions', 'updated_at',
               existing_type=postgresql.TIMESTAMP(),
               nullable=False)
    op.drop_constraint(None, 'subscribes', type_='unique')
    # ### end Alembic commands ###
