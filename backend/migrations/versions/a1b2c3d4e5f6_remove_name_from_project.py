"""Remove name from Project

Revision ID: a1b2c3d4e5f6
Revises: 1482cf11f222
Create Date: 2025-12-07 12:00:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "1482cf11f222"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("project", "name")


def downgrade() -> None:
    op.add_column("project", sa.Column("name", sa.VARCHAR(), nullable=False))
