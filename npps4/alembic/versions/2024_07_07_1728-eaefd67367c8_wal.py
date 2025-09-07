"""wal

Revision ID: eaefd67367c8
Revises: 1d73d9b010d0
Create Date: 2024-07-07 17:28:38.375308

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "eaefd67367c8"
down_revision: Union[str, None] = "1d73d9b010d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_bind().engine.name.startswith("sqlite"):
        op.execute("PRAGMA journal_mode=WAL;")


def downgrade() -> None:
    if op.get_bind().engine.name.startswith("sqlite"):
        op.execute("PRAGMA journal_mode=DELETE;")
