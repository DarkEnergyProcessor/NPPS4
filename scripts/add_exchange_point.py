import npps4.script_dummy  # isort:skip

import argparse

import npps4.idol
import npps4.system.exchange
import npps4.db.exchange
import npps4.scriptutils.user


async def is_exchange_point_id_valid(context: npps4.idol.BasicSchoolIdolContext, exchange_point_id: int):
    result = await context.db.exchange.get(npps4.db.exchange.ExchangePoint, exchange_point_id)
    return result is not None


async def run_script(arg: list[str]):
    parser = argparse.ArgumentParser(__file__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    npps4.scriptutils.user.register_args(group)
    parser.add_argument("exchange_point_id", type=int, help="Exchange point ID.")
    parser.add_argument("amount", type=int, default=0, nargs="?", help="Amount of exchange point to add.")
    args = parser.parse_args(arg)

    async with npps4.idol.BasicSchoolIdolContext(lang=npps4.idol.Language.en) as context:
        target_user = await npps4.scriptutils.user.from_args(context, args)
        if not await is_exchange_point_id_valid(context, args.exchange_point_id):
            raise Exception("no such exchange point ID")

        exchange_point = await npps4.system.exchange.get_exchange_point(
            context, target_user, args.exchange_point_id, True
        )
        assert exchange_point is not None

        print("Old:", exchange_point.amount)
        exchange_point.amount = max(exchange_point.amount + args.amount, 0)
        print("New:", exchange_point.amount)


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
