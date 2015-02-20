"""
This revision is used for adding column ``errmsg``
to table ```containers```.

Revision ID: 2ed10d656484
Revises: 32bf947e2447
Create Date: 2015-02-12 22:45:27.144688

"""

# revision identifiers, used by Alembic.
revision = '2ed10d656484'
down_revision = '32bf947e2447'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, String


def upgrade():
    op.add_column("containers",
        Column("errmsg",String(500))
    )

def downgrade():
    op.drop_column("containers","errmsg")
