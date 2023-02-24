import hashlib
import json
import os
import zipfile

import libhonoka


EXTERNAL_DATA_ROOT = "data/external/"


def main(download_data):
    if download_data is None:
        with open("download-temp/download_data.json", "r", encoding="UTF-8") as f:
            download_data = json.load(f)
    zipfiles = []
    for data in download_data:
        filename = "download-temp/" + hashlib.md5(data["url"].encode("UTF-8")).hexdigest() + ".zip"
        zipfiles.append(filename)
        with zipfile.ZipFile(filename, "r") as archive:
            print(f"Loading {filename}")
            file_map = {}  # type: dict[str, zipfile.ZipInfo]
            for infos in archive.infolist():
                if infos.filename.startswith("en/"):
                    dest = EXTERNAL_DATA_ROOT + infos.filename[3:]
                    file_map[dest] = infos
                else:
                    dest = EXTERNAL_DATA_ROOT + infos.filename
                    if dest in file_map:
                        if not file_map[dest].filename.startswith("en/"):
                            file_map[dest] = infos
                    else:
                        file_map[dest] = infos
            for dest, info in file_map.items():
                if info.file_size > 0:
                    print(f"Extracting {info.filename}")
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with archive.open(info, "r") as f:
                        filedata = f.read()
                        dctx = libhonoka.Dctx(dest, filedata[:16])
                        with open(dest, "wb") as f2:
                            f2.write(dctx.decrypt_block(filedata[16:]))
                else:
                    print(f"Deleting {dest}")
                    try:
                        os.remove(dest)
                    except FileNotFoundError:
                        pass
    for f in zipfiles:
        os.remove(f)
    os.remove("download-temp/download_data.json")


if __name__ == "__main__":
    main(None)
