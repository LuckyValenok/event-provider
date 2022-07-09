"""'rating_system2'

Revision ID: d7cb2a2628fa
Revises: 37ff82f5f82c
Create Date: 2022-07-09 17:14:08.133035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd7cb2a2628fa'
down_revision = '37ff82f5f82c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_rate',
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('org_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['org_id'], ['user.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_user_rate_org_id'), 'user_rate', ['org_id'], unique=False)
    op.create_index(op.f('ix_user_rate_user_id'), 'user_rate', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_rate_user_id'), table_name='user_rate')
    op.drop_index(op.f('ix_user_rate_org_id'), table_name='user_rate')
    op.drop_table('user_rate')
    # ### end Alembic commands ###