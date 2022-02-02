"""CourseBuilding and Time column

Revision ID: e8bd9a6571b1
Revises: 0ffc081126a8
Create Date: 2022-01-15 12:29:19.150364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8bd9a6571b1'
down_revision = '0ffc081126a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('course', sa.Column('building', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('course', 'building')
    # ### end Alembic commands ###