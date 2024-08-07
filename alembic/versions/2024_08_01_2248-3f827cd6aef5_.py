"""empty message

Revision ID: 3f827cd6aef5
Revises: eaefd67367c8
Create Date: 2024-08-01 22:48:15.838659

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3f827cd6aef5"
down_revision: Union[str, None] = "eaefd67367c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "exchange_item_limit",
        sa.Column("id", sa.BigInteger().with_variant(sa.INTEGER(), "sqlite"), nullable=False),
        sa.Column("user_id", sa.BigInteger().with_variant(sa.INTEGER(), "sqlite"), nullable=False),
        sa.Column("exchange_item_id", sa.BigInteger().with_variant(sa.INTEGER(), "sqlite"), nullable=False),
        sa.Column("count", sa.BigInteger().with_variant(sa.INTEGER(), "sqlite"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "exchange_item_id"),
    )
    with op.batch_alter_table("exchange_item_limit", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_exchange_item_limit_exchange_item_id"), ["exchange_item_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_exchange_item_limit_user_id"), ["user_id"], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("exchange_item_limit", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_exchange_item_limit_user_id"))
        batch_op.drop_index(batch_op.f("ix_exchange_item_limit_exchange_item_id"))

    op.drop_table("exchange_item_limit")
    # ### end Alembic commands ###
