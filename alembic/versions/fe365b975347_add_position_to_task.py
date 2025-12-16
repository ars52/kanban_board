"""add_position_to_task

Revision ID: fe365b975347
Revises: c61d2575282d
Create Date: 2025-12-08 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe365b975347'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('task', sa.Column('position', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('task', 'position')
