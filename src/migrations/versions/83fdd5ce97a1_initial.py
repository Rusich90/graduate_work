"""Initial

Revision ID: 83fdd5ce97a1
Revises: 
Create Date: 2022-05-23 08:31:59.765933

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '83fdd5ce97a1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subscribe_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('price', sa.SmallInteger(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscribe_types_id'), 'subscribe_types', ['id'], unique=False)
    op.create_table('transactions',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('subscribe_type_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.SmallInteger(), nullable=True),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('failed_reason', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['subscribe_type_id'], ['subscribe_types.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('subscribes',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('subscribe_type_id', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.DateTime(), nullable=False),
    sa.Column('end_date', sa.DateTime(), nullable=False),
    sa.Column('auto_renewal', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['subscribe_type_id'], ['subscribe_types.id'], ),
    sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscribes')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_subscribe_types_id'), table_name='subscribe_types')
    op.drop_table('subscribe_types')
    # ### end Alembic commands ###
