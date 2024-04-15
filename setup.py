import os.path
import setuptools

import npps4.version

with open(os.path.join(os.path.dirname(__file__), "requirements.txt"), "r", encoding="utf-8") as f:
    setuptools.setup(
        name="npps4",
        version="%d.%d.%d" % npps4.version.NPPS4_VERSION,
        description="Null-Pointer Private Server",
        author="Miku AuahDark",
        packages=["npps4"],
        install_requires=["wheel", *map(str.strip, f)],
        entry_points={"console_scripts": ["npps4_script=npps4.script:entry"]},
    )
