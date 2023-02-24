import hashlib
import json
import os

import httpx

import apply_update_data


def main(download_data):
    if download_data is None:
        with open("download-temp/download_data.json", "r", encoding="UTF-8") as f:
            download_data = json.load(f)
    print("Total download size", sum(map(lambda x: int(x["size"]), download_data)), "bytes")
    session = None
    dlcount = len(download_data)
    i = 0
    for data in download_data:
        i = i + 1
        filename = hashlib.md5(data["url"].encode("UTF-8")).hexdigest() + ".zip"
        if not os.path.exists(filename):
            if session is None:
                session = httpx.Client()
            print(f"Downloading {i}/{dlcount}")
            response = session.get(data["url"])
            if response.status_code != 200:
                raise Exception(f"Download failed for {data['url']}")
            with open(f"download-temp/{filename}", "wb") as f:
                f.write(response.content)
    apply_update_data.main(download_data)


if __name__ == "__main__":
    main(None)
