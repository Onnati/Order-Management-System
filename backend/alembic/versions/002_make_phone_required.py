"""Make customer phone required

Revision ID: 002_phone_required
Revises: 001_initial
Create Date: 2026-06-19

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "002_phone_required"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE customers SET phone = '' WHERE phone IS NULL")
    op.alter_column("customers", "phone", existing_type=sa.String(length=32), nullable=False)


def downgrade() -> None:
    op.alter_column("customers", "phone", existing_type=sa.String(length=32), nullable=True)
