"""
This revision is used for adding column ``errmsg``
for table ``images``.

Revision ID: 32bf947e2447
Revises: 
Create Date: 2015-02-12 22:16:03.800164

"""

# revision identifiers, used by Alembic.
revision = '32bf947e2447'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String


def upgrade():
    op.add_column('images',
        Column('errmsg',String(500))
    )

def downgrade():
    op.drop_column('images','errmsg')
