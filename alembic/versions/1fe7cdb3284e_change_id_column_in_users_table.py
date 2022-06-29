"""change id column in users table

Revision ID: 1fe7cdb3284e
Revises: 048217f424a5
Create Date: 2022-06-29 09:15:05.022577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1fe7cdb3284e'
down_revision = '048217f424a5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', column_name='id', autoincrement=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', column_name='id', autoincrement=True)
    # ### end Alembic commands ###
