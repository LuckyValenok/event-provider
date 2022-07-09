"""change column to enum in user table

Revision ID: 0410f803f03a
Revises: fc9a37f3bc70
Create Date: 2022-06-30 09:23:13.012033

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '0410f803f03a'
down_revision = 'fc9a37f3bc70'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('rank', sa.Enum('USER', 'MODER', 'ORGANIZER', 'ADMIN', name='rank'),
                                    nullable=True))
    op.add_column('user', sa.Column('step', sa.Enum('NONE', 'FIRST_NAME', 'MIDDLE_NAME', name='step'),
                                    nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'step')
    op.drop_column('user', 'rank')
    # ### end Alembic commands ###
