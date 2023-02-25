import json
import os

import sifemu
import download_update_data


class DownloadUpdate(sifemu.SIFEmuRequest):
    def __init__(
        self,
        *,
        os: str | None = None,
        install_version: str | None = None,
        package_list: list[int] | None = None,
        external_version: str | None = None,
    ):
        super().__init__("download", "update")
        self.os = os
        self.install_version = install_version
        self.package_list = package_list or []
        self.external_version = external_version

    def add_more_context(self, sifemu: sifemu.SIFEmu):
        if self.os is None:
            self.os = sifemu.get_os()
        if self.os not in ("iOS", "Android"):
            raise ValueError("OS must be either iOS or Android")
        if self.install_version is None:
            clientver = sifemu.get_client_version()
            lastdot = clientver.rfind(".")
            if lastdot == -1:
                raise Exception("Cannot autodetermine install version")
            self.install_version = clientver[:lastdot] + ".0"
        if self.external_version is None:
            self.external_version = sifemu.get_client_version()

    def get_data(self):
        return {
            "target_os": self.os,
            "install_version": self.install_version,
            "external_version": self.external_version,
            "package_list": self.package_list,
        }


class DownloadBatch(sifemu.SIFEmuRequest):
    def __init__(
        self,
        package_type: int,
        excluded_package_ids: list[int] | None = None,
        *,
        client_version: str | None = None,
        os: str | None = None,
    ):
        super().__init__("download", "batch")
        self.package_type = package_type
        self.exclude = excluded_package_ids or []
        self.client_version = client_version
        self.os = os

    def add_more_context(self, sifemu: sifemu.SIFEmu):
        if self.os is None:
            self.os = sifemu.get_os()
        if self.os not in ("iOS", "Android"):
            raise ValueError("OS must be either iOS or Android")
        if self.client_version is None:
            self.client_version = sifemu.get_client_version()

    def get_data(self):
        return {
            "client_version": self.client_version,
            "os": self.os,
            "package_type": self.package_type,
            "excluded_package_ids": self.exclude,
        }


class DownloadAdditional(sifemu.SIFEmuRequest):
    def __init__(
        self,
        package_type: int,
        package_id: int,
        *,
        client_version: str | None = None,
        os: str | None = None,
    ):
        super().__init__("download", "additional")
        self.package_type = package_type
        self.package_id = package_id
        self.client_version = client_version
        self.os = os

    def add_more_context(self, sifemu: sifemu.SIFEmu):
        if self.os is None:
            self.os = sifemu.get_os()
        if self.os not in ("iOS", "Android"):
            raise ValueError("OS must be either iOS or Android")
        if self.client_version is None:
            self.client_version = sifemu.get_client_version()

    def get_data(self):
        return {
            "client_version": self.client_version,
            "target_os": self.os,
            "type": "0",
            "package_type": self.package_type,
            "package_id": self.package_id,
            "region": "392",
        }


class UserInfo(sifemu.SIFEmuRequest):
    def __init__(self):
        super().__init__("user", "userInfo")


try:
    with open("data/external/config/server_info.json", "r", encoding="UTF-8") as f:
        external_server_info = json.load(f)
except FileNotFoundError:
    external_server_info = None


with open("data/install/config/server_info.json", "r", encoding="UTF-8") as f:
    install_server_info = json.load(f)

with open("credentials.json", "r", encoding="UTF-8") as f:
    credentials = json.load(f)

os.makedirs("download-temp", exist_ok=True)

if os.path.exists("download-temp/download_data.json"):
    raise Exception("Update is in progress. Forgot to call `apply_update_data.py`?")


if external_server_info is None:
    external_server_info = install_server_info


external_client_version = tuple(map(int, external_server_info["server_version"].split(".")))
install_client_version = tuple(map(int, install_server_info["server_version"].split(".")))

if install_client_version > external_client_version:
    client_version = "%d.%d" % install_client_version
else:
    client_version = "%d.%d" % external_client_version


print("Client version", client_version)

sif = sifemu.SIFEmu(application_id=external_server_info["application_key"].encode("UTF-8"))
sif.set_bundle_version("9.11")
sif.set_os_ios("iPad13_8 iPad 16.2")
sif.set_username(credentials["LOVELIVE_ID"])
sif.set_password(credentials["LOVELIVE_PW"])
sif.set_client_version(client_version)
print("/login/authkey")
sif.initial_token()
print("/login/login")
sif.login()

print("/user/userInfo")
response = sif.request(UserInfo())
if not sif.is_need_update():
    print("Up-to-date!")
    if __name__ == "__main__":
        raise SystemExit(0)


if __name__ == "__main__":
    print("/download/update")
    response = sif.request(
        DownloadUpdate(
            os="iOS",
            install_version=install_server_info["server_version"],
            external_version=external_server_info["server_version"],
        )
    )
    download_update_data.main(response)

__all__ = ["sif", "DownloadBatch", "DownloadAdditional"]
