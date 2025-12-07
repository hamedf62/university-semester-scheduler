"""add project_id to teacher_availability

Revision ID: f1e2d3c4b5a6
Revises: 1271601eeb5a
Create Date: 2025-12-07 19:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f1e2d3c4b5a6"
down_revision: Union[str, Sequence[str], None] = "1271601eeb5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Recreate table to include project_id in PK
    op.drop_table("teacheravailability")
    op.create_table(
        "teacheravailability",
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("timeslot_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["teacher.id"],
        ),
        sa.ForeignKeyConstraint(
            ["timeslot_id"],
            ["timeslot.id"],
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
        ),
        sa.PrimaryKeyConstraint("teacher_id", "timeslot_id", "project_id"),
    )


def downgrade() -> None:
    op.drop_table("teacheravailability")
    op.create_table(
        "teacheravailability",
        sa.Column("teacher_id", sa.Integer(), nullable=False),
        sa.Column("timeslot_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["teacher.id"],
        ),
        sa.ForeignKeyConstraint(
            ["timeslot_id"],
            ["timeslot.id"],
        ),
        sa.PrimaryKeyConstraint("teacher_id", "timeslot_id"),
    )
