"""add watering_interval_days to plants

Revision ID: b1c2d3e4f5a6
Revises: ae50b3e28cd1
Create Date: 2026-06-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'ae50b3e28cd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'plants',
        sa.Column('watering_interval_days', sa.Integer(), nullable=True),
        schema='public',
    )


def downgrade() -> None:
    op.drop_column('plants', 'watering_interval_days', schema='public')
