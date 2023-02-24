import os

import Cryptodome.PublicKey.RSA


def ask_confirm(prompt: str):
    while True:
        confirm = input(f"{prompt} [y/n] ")
        confirm_lower = confirm.lower()
        if confirm_lower == "y":
            return True
        elif confirm_lower == "n":
            return False
        else:
            print("Please type `y' or `n'!")


if os.path.exists("server_key.pem"):
    if not ask_confirm("WARNING: server_key.pem already exist. Are you sure want to overwrite the server key?"):
        raise SystemExit(0)
    # Ask user again to make sure
    if not ask_confirm("WARNING WARNING: YOU HAVE BEEN WARNED! ARE YOU SURE? THE KEY WILL BE OVERWRITTEN!!!"):
        raise SystemExit(0)

key = Cryptodome.PublicKey.RSA.generate(1024)
with open("server_key.pem", "wb") as f:
    f.write(key.export_key("PEM"))
