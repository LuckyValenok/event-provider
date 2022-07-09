"""'add_rating_column_to_user_table'

Revision ID: c31e1e55ffa3
Revises: 7551be765176
Create Date: 2022-07-09 15:22:33.650597

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c31e1e55ffa3'
down_revision = '7551be765176'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('rating', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'rating')
    # ### end Alembic commands ###