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
            for info in archive.infolist():
                dest = EXTERNAL_DATA_ROOT + info.filename
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
