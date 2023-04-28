"""Initial model

Revision ID: c4e3ad6d739f
Revises: 
Create Date: 2023-04-27 23:44:09.074508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c4e3ad6d739f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger().with_variant(sa.INTEGER(), "sqlite"), nullable=False),
        sa.Column("key", sa.String(length=1024), nullable=True),
        sa.Column("passwd", sa.String(length=1024), nullable=True),
        sa.Column("name", sa.String(length=1024), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("exp", sa.Integer(), nullable=False),
        sa.Column("previous_exp", sa.Integer(), nullable=False),
        sa.Column("next_exp", sa.Integer(), nullable=False),
        sa.Column("game_coin", sa.Integer(), nullable=False),
        sa.Column("free_sns_coin", sa.Integer(), nullable=False),
        sa.Column("paid_sns_coin", sa.Integer(), nullable=False),
        sa.Column("social_point", sa.Integer(), nullable=False),
        sa.Column("unit_max", sa.Integer(), nullable=False),
        sa.Column("waiting_unit_max", sa.Integer(), nullable=False),
        sa.Column("energy_max", sa.Integer(), nullable=False),
        sa.Column("energy_full_time", sa.BigInteger().with_variant(sa.INTEGER(), "sqlite"), nullable=False),
        sa.Column("license_live_energy_recoverly_time", sa.Integer(), nullable=False),
        sa.Column("energy_full_need_time", sa.BigInteger().with_variant(sa.INTEGER(), "sqlite"), nullable=False),
        sa.Column("over_max_energy", sa.Integer(), nullable=False),
        sa.Column("training_energy", sa.Integer(), nullable=False),
        sa.Column("training_energy_max", sa.Integer(), nullable=False),
        sa.Column("friend_max", sa.Integer(), nullable=False),
        sa.Column("invite_code", sa.Integer(), nullable=False),
        sa.Column("insert_date", sa.BigInteger().with_variant(sa.INTEGER(), "sqlite"), nullable=False),
        sa.Column("update_date", sa.BigInteger().with_variant(sa.INTEGER(), "sqlite"), nullable=False),
        sa.Column("tutorial_state", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_user_invite_code"), ["invite_code"], unique=False)
        batch_op.create_index(batch_op.f("ix_user_key"), ["key"], unique=False)

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_user_key"))
        batch_op.drop_index(batch_op.f("ix_user_invite_code"))

    op.drop_table("user")
    # ### end Alembic commands ###