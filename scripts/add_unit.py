import argparse

import sqlalchemy

import npps4.idol
import npps4.idol.system.unit
import npps4.db.main
import npps4.db.unit
import npps4.scriptutils.user


def intrange(minval: int, maxval: int):
    r = range(minval, maxval + 1)

    def wrap(v):
        nonlocal r
        intval = int(v)
        if intval not in r:
            raise ValueError(f"value {intval} out-of-range")
        return intval

    return wrap


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    npps4.scriptutils.user.register_args(group)
    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument("--unit-id", type=int, help="Internal unit ID to give")
    group2.add_argument("--unit-number", type=int, help="Album card number to give (card number in-game)")
    parser.add_argument("-l", "--level", type=int, default=1, help="Card level (ignored for support cards)")
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Forcefully add card even if user inventory is full (ignored for support cards).",
    )
    parser.add_argument(
        "-w",
        "--waiting-room",
        action="store_true",
        help="Put the card in waiting room instead in active room (ignored for support cards).",
    )
    parser.add_argument("-z", "--idolize", action="store_true", help="Idolize the card when possible.")
    parser.add_argument("-c", "--amount", type=intrange(1, 1000000), default=1, help="Amount of cards to add.")
    parser.add_argument(
        "--add-sis-slot",
        type=intrange(0, 4),
        default=0,
        help="Additional amount of SIS slot to unlock (automatically clamped; ignored for support cards).",
    )
    parser.add_argument("--signed", action="store_true", help="Give card signed by the character, when possible.")
    args = parser.parse_args(arg)

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        target_user = await npps4.scriptutils.user.from_args(context, args)

        if args.unit_id is None:
            # Look at unit_number
            q = sqlalchemy.select(npps4.db.unit.Unit).where(npps4.db.unit.Unit.unit_number == args.unit_number)
            unit_info = (await context.db.unit.execute(q)).scalar()
        else:
            unit_info = await context.db.unit.get(npps4.db.unit.Unit, args.unit_id)

        if unit_info is None:
            raise Exception("unit does not exist")

        if unit_info.disable_rank_up > 0:
            # Support cards
            await npps4.idol.system.unit.add_supporter_unit(context, target_user, unit_info.unit_id, args.amount)
        else:
            if not args.force:
                unit_count = await npps4.idol.system.unit.count_units(context, target_user, not args.waiting_room)
                if (unit_count + args.amount) > (
                    target_user.waiting_unit_max if args.waiting_room else target_user.unit_max
                ):
                    raise Exception("User inventory is full")

            # Mark idolized
            pre_idolized = unit_info.rank_min == unit_info.rank_max

            # Get rarity info
            unit_rarity = await npps4.idol.system.unit.get_unit_rarity(context, unit_info.rarity)
            assert unit_rarity is not None

            # Clamp level
            unit_level: int = min(
                args.level,
                unit_rarity.after_level_max if pre_idolized or args.idolize else unit_rarity.before_level_max,
            )

            # Get EXP needed
            unit_level_up_pattern = await npps4.idol.system.unit.get_unit_level_up_pattern(context, unit_info)
            unit_exp = npps4.idol.system.unit.get_exp_for_target_level(unit_info, unit_level_up_pattern, unit_level)
            unit_signed = bool(
                args.signed and await npps4.idol.system.unit.has_signed_variant(context, unit_info.unit_id)
            )

            for _ in range(args.amount):
                unit_data = await npps4.idol.system.unit.create_unit(
                    context, target_user, unit_info.unit_id, not args.waiting_room
                )
                assert unit_data is not None

                if not pre_idolized and args.idolize:
                    await npps4.idol.system.unit.idolize(context, target_user, unit_data)

                unit_data.is_signed = unit_signed
                unit_data.exp = unit_exp
                unit_data.unit_removable_skill_capacity = min(
                    unit_info.default_removable_skill_capacity + int(args.add_sis_slot),
                    unit_info.max_removable_skill_capacity,
                )
                await npps4.idol.system.unit.add_unit_by_object(context, target_user, unit_data)
