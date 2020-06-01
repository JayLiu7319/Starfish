"""Create test entity table

Revision ID: 308463f02e7a
Revises: 
Create Date: 2020-03-04 22:11:09.331965

"""
import sqlalchemy as sa
from alembic import op
from oslo_utils import uuidutils, timeutils

# revision identifiers, used by Alembic.
revision = '308463f02e7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'test_entity',
        sa.Column('id', sa.String(36), primary_key=True, default=uuidutils.generate_uuid),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('manage_ip', sa.String(64), nullable=False),
        sa.Column('created_at', sa.DateTime, default=lambda: timeutils.utcnow()),
        sa.Column('updated_at', sa.DateTime, onupdate=lambda: timeutils.utcnow())
    )


def downgrade():
    op.drop_table('test_entity')
