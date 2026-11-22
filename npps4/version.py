import importlib.metadata

NPPS4_VERSION: tuple[int, int, int]
"""NPPS4 version is formatted as `YYYY.MMDD.N`. `MMDD` is not zero-padded, so `2027.101` is valid for 1 January 2027."""

try:
    # Read importlib directly
    _v = importlib.metadata.version("npps4").split(".")
    NPPS4_VERSION = (int(_v[0]), int(_v[1]), int(_v[2]))

except importlib.metadata.PackageNotFoundError:
    # Try reading the pyproject.toml
    import os
    import tomllib

    pyproject = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
    try:
        with open(pyproject, "rb") as f:
            pyproject_data = tomllib.load(f)
    except IOError:
        # Real fallback, means unknown.
        NPPS4_VERSION = (0, 0, 0)
    else:
        _v0: str = pyproject_data["project"]["version"]
        _v = _v0.split(".")
        NPPS4_VERSION = (int(_v[0]), int(_v[1]), int(_v[2]))
