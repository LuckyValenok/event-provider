"""added image column to achievement table

Revision ID: 8ef90f1a9881
Revises: 7551be765176
Create Date: 2022-07-09 16:10:52.615745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ef90f1a9881'
down_revision = '7551be765176'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('achievement', sa.Column('image', sa.BLOB(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('achievement', 'image')
    # ### end Alembic commands ###