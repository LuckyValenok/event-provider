"""added index to achievement, interest and local_group tables

Revision ID: c5580c6918fd
Revises: 1aa7c6b146f9
Create Date: 2022-07-03 16:03:31.786995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c5580c6918fd'
down_revision = '1aa7c6b146f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_achievement_name'), 'achievement', ['name'], unique=False)
    op.create_index(op.f('ix_interest_name'), 'interest', ['name'], unique=False)
    op.create_index(op.f('ix_local_group_name'), 'local_group', ['name'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_local_group_name'), table_name='local_group')
    op.drop_index(op.f('ix_interest_name'), table_name='interest')
    op.drop_index(op.f('ix_achievement_name'), table_name='achievement')
    # ### end Alembic commands ###