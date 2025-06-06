"""empty message

Revision ID: d701309ff89e
Revises: 475147102361
Create Date: 2025-05-03 18:34:45.211213

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d701309ff89e"
down_revision: Union[str, None] = "475147102361"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("album", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_album_favorite_point"), ["favorite_point"], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("album", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_album_favorite_point"))

    # ### end Alembic commands ###
