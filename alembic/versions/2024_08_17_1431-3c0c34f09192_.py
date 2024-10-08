"""empty message

Revision ID: 3c0c34f09192
Revises: 3f827cd6aef5
Create Date: 2024-08-17 14:31:59.537269

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3c0c34f09192"
down_revision: Union[str, None] = "3f827cd6aef5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("session", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_session_last_accessed"), ["last_accessed"], unique=False)
        batch_op.create_index(batch_op.f("ix_session_user_id"), ["user_id"], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("session", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_session_user_id"))
        batch_op.drop_index(batch_op.f("ix_session_last_accessed"))

    # ### end Alembic commands ###
