import npps4.script_dummy  # isort:skip

import base64

import npps4.data
import npps4.data.schema
import npps4.util


async def run_script(args: list[str]):
    input_code = args[0]
    server_data = npps4.data.get()

    for serial_code in server_data.serial_codes:
        if serial_code.check_serial_code(input_code):
            if isinstance(serial_code.serial_code, str):
                raise Exception("cannot encrypt action without secure serial code")

            print(input_code)
            print()
            input_data = serial_code.get_action(input_code).model_dump_json(exclude_defaults=True)
            print(input_data)
            return

    raise Exception("cannot find such serial code")


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
