import os

with open("config.sample.toml", "r", encoding="utf-8", newline="") as f:
    config = f.read()

config = config.replace(
    'server_private_key = "default_server_key.pem"', 'server_private_key = "server_key.pem"'
).replace('server_data = "npps4/server_data.json"', 'server_data = "server_data.json"')

dlapi_server = os.environ.get("NPPS4_CONFIG_DOWNLOAD_N4DLAPI_SERVER", "")
if dlapi_server:
    config = config.replace('backend = "none"', 'backend = "n4dlapi"').replace(
        'server = "https://localhost:8000"', f'server = "{dlapi_server}"'
    )

with open("dist/npps4/config.toml", "w", encoding="utf-8", newline="") as f:
    f.write(config)
