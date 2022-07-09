"""'create_userfriend_table'

Revision ID: 844be4048b87
Revises: 126cb69213b1
Create Date: 2022-07-08 23:45:46.358857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '844be4048b87'
down_revision = '126cb69213b1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_friends',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('friend_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['friend_id'], ['user.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_user_friends_friend_id'), 'user_friends', ['friend_id'], unique=False)
    op.create_index(op.f('ix_user_friends_user_id'), 'user_friends', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_friends_user_id'), table_name='user_friends')
    op.drop_index(op.f('ix_user_friends_friend_id'), table_name='user_friends')
    op.drop_table('user_friends')
    # ### end Alembic commands ###
