"""empty message

Revision ID: 1d73d9b010d0
Revises: a7561a269dac
Create Date: 2024-05-12 11:09:56.034624

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1d73d9b010d0"
down_revision: Union[str, None] = "a7561a269dac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "normal_live_unlock",
        sa.Column("id", sa.BigInteger().with_variant(sa.INTEGER(), "sqlite"), nullable=False),
        sa.Column("user_id", sa.BigInteger().with_variant(sa.INTEGER(), "sqlite"), nullable=False),
        sa.Column("live_track_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "live_track_id"),
    )
    with op.batch_alter_table("normal_live_unlock", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_normal_live_unlock_live_track_id"), ["live_track_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_normal_live_unlock_user_id"), ["user_id"], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("normal_live_unlock", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_normal_live_unlock_user_id"))
        batch_op.drop_index(batch_op.f("ix_normal_live_unlock_live_track_id"))

    op.drop_table("normal_live_unlock")
    # ### end Alembic commands ###
