"""added columns description and date to event table

Revision ID: 1aa7c6b146f9
Revises: 904bffbd0b91
Create Date: 2022-06-30 19:18:33.691356

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '1aa7c6b146f9'
down_revision = '904bffbd0b91'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('event', sa.Column('description', sa.VARCHAR(length=255), nullable=True))
    op.add_column('event', sa.Column('date', sa.TIMESTAMP(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('event', 'date')
    op.drop_column('event', 'description')
    # ### end Alembic commands ###
