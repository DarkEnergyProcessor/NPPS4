import base64

import npps4.script_dummy
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

            input_data = serial_code.get_action(input_code).model_dump_json(exclude_defaults=True)
            key = npps4.data.schema.derive_serial_code_action_key(input_code, serial_code.serial_code.salt)
            aes = npps4.data.schema.initialize_aes_for_action_field(key, serial_code.serial_code.salt)
            encrypted = aes.encrypt(input_data.encode("utf-8"))
            encrypted_b64 = str(base64.urlsafe_b64encode(encrypted), "utf-8")

            print("encrypted")
            for i in range(0, len(encrypted_b64), 80):
                print(encrypted_b64[i : i + 80])

            # Test
            aes = npps4.data.schema.initialize_aes_for_action_field(key, serial_code.serial_code.salt)
            decrypted = aes.decrypt(encrypted)
            decrypted_type = npps4.data.schema.SERIAL_CODE_ACTION_ADAPTER.validate_json(decrypted)
            print()
            print("decrypted")
            print(str(decrypted, "utf-8"))
            print(type(decrypted_type), decrypted_type)
            return

    raise Exception("cannot find such serial code")


if __name__ == "__main__":
    import npps4.scriptutils.boot

    npps4.scriptutils.boot.start(run_script)
