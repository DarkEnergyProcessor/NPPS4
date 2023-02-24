# Implements SIF JP v3 and v4 decryption mechanism
import hashlib
import os

NAME_PREFIX = b"Hello"
KEY_TABLES = [
    1210253353,
    1736710334,
    1030507233,
    1924017366,
    1603299666,
    1844516425,
    1102797553,
    32188137,
    782633907,
    356258523,
    957120135,
    10030910,
    811467044,
    1226589197,
    1303858438,
    1423840583,
    756169139,
    1304954701,
    1723556931,
    648430219,
    1560506399,
    1987934810,
    305677577,
    505363237,
    450129501,
    1811702731,
    2146795414,
    842747461,
    638394899,
    51014537,
    198914076,
    120739502,
    1973027104,
    586031952,
    1484278592,
    1560111926,
    441007634,
    1006001970,
    2038250142,
    232546121,
    827280557,
    1307729428,
    775964996,
    483398502,
    1724135019,
    2125939248,
    742088754,
    1411519905,
    136462070,
    1084053905,
    2039157473,
    1943671327,
    650795184,
    151139993,
    1467120569,
    1883837341,
    1249929516,
    382015614,
    1020618905,
    1082135529,
    870997426,
    1221338057,
    1623152467,
    1020681319,
]


class KeyTables:
    def __init__(self, a: int, c: int, s: int):
        self.a = a
        self.c = c
        self.shift = s

    def next(self, x: int):
        return (x * self.a + self.c) & 0xFFFFFFFF


V4_LCG_PARAM = [
    KeyTables(1103515245, 12345, 15),
    KeyTables(22695477, 1, 23),
    KeyTables(214013, 2531011, 24),
    KeyTables(65793, 4282663, 8),
]


class Dctx:
    def __init__(self, filename: str, header: bytes):
        if len(header) < 16:
            raise ValueError("Header must be 16 bytes!")

        fullhashed = NAME_PREFIX + os.path.basename(filename).encode("UTF-8")
        md5hash = hashlib.md5(fullhashed).digest()
        if header[0] == (~md5hash[4] & 255) and header[1] == (~md5hash[5] & 255) and header[2] == (~md5hash[6] & 255):
            if header[7] > 2:
                raise NotImplementedError("V5+ not implemented")
            elif header[7] == 2:
                self.lcg = V4_LCG_PARAM[header[6]]
                self.init_key = (md5hash[8] << 24) | (md5hash[9] << 16) | (md5hash[10] << 8) | md5hash[11]
            else:
                key_index = (header[10] << 8) | header[11]
                ka = sum(fullhashed)

                if ka != key_index:
                    raise ValueError("Key index name mismatch")
                self.lcg = V4_LCG_PARAM[2]  # MSVC
                self.init_key = KEY_TABLES[key_index & 0x3F]
                if header[7] == 1:
                    self.init_key = (~self.init_key) & 0xFFFFFFFF
            self.update_key = self.init_key
            self.pos = 0
        else:
            raise ValueError("Invalid decrypt header")

    def decrypt_int(self, data: int):
        result = (data & 0xFF) ^ ((self.update_key >> self.lcg.shift) & 0xFF)
        self.pos = self.pos + 1
        self._step()
        return result

    def decrypt_block(self, data: bytes):
        return bytes(map(lambda x: self.decrypt_int(x), data))

    def _step(self):
        self.update_key = self.lcg.next(self.update_key)
