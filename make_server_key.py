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


def print_public_key(key: Cryptodome.PublicKey.RSA.RsaKey):
    print(str(key.public_key().export_key("PEM"), "UTF-8"))


if os.path.exists("server_key.pem"):
    with open("server_key.pem", "r", encoding="UTF-8") as f:
        key = Cryptodome.PublicKey.RSA.import_key(f.read())
        print_public_key(key)
    if not ask_confirm("WARNING: server_key.pem already exist. Overwrite?"):
        print("Key not overwritten")
        raise SystemExit(0)
    # Ask user again to make sure
    if not ask_confirm("WARNING WARNING: YOU HAVE BEEN WARNED! ARE YOU SURE? THE KEY WILL BE OVERWRITTEN!!!"):
        print("Key not overwritten")
        raise SystemExit(0)

key = Cryptodome.PublicKey.RSA.generate(1024)
with open("server_key.pem", "wb") as f:
    f.write(key.export_key("PEM"))

print_public_key(key)
