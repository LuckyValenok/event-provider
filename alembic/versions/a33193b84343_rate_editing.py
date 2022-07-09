"""'rate_editing'

Revision ID: a33193b84343
Revises: c31e1e55ffa3
Create Date: 2022-07-09 16:59:18.528364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a33193b84343'
down_revision = 'c31e1e55ffa3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('achievement', sa.Column('image', sa.BLOB(), nullable=False))
    op.drop_column('user', 'rating')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('rating', sa.INTEGER(), nullable=True))
    op.drop_column('achievement', 'image')
    # ### end Alembic commands ###
