_RELEASE_KEYS: dict[int, str] = {}

get = _RELEASE_KEYS.get
update = _RELEASE_KEYS.update


def formatted():
    global _RELEASE_KEYS
    return [{"id": k, "key": v} for k, v in _RELEASE_KEYS.items()]
