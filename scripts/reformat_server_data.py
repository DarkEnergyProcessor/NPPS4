import npps4.script_dummy  # Must be first
import npps4.data.schema


async def run_script(args: list[str]):
    npps4.data.update()


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
