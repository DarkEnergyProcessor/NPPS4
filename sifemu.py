import base64
import hashlib
import hmac
import json
import secrets
import time
import urllib.parse
import uuid

from typing import Any, cast


RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBpUMUVjHWNI5q3ZRjF1vPnh+m
aEGdbZkeosVvzLytBy9eYJ9qLYyFXxOY1LiggWyOLS+xEVMpV3A6frI3VewkVuCw
na52ssCZcQSBA03Ykeb/cfHk5ChsDUP1vmAbloMb9f++Dow6Z4yubFWmBVMCHA6l
fiUDPHjI8JqG56XJKQIDAQAB
-----END PUBLIC KEY-----
"""

try:
    import Cryptodome
    import Cryptodome.Cipher
    import Cryptodome.Cipher.AES
    import Cryptodome.Cipher.PKCS1_v1_5
    import Cryptodome.PublicKey
    import Cryptodome.PublicKey.RSA
    import Cryptodome.Util
    import Cryptodome.Util.Padding

    CRYPTO_BACKEND = "PyCryptodomex"

    def aes_encrypt(iv: bytes, key: bytes, data: bytes):
        aes = Cryptodome.Cipher.AES.new(key, Cryptodome.Cipher.AES.MODE_CBC, iv)
        return iv + aes.encrypt(Cryptodome.Util.Padding.pad(data, 16))

    load_rsa = Cryptodome.PublicKey.RSA.import_key  # type: ignore

    def rsa_encrypt(rsa: Cryptodome.PublicKey.RSA.RsaKey, data: bytes):  # type: ignore
        pkcs1_pad = Cryptodome.Cipher.PKCS1_v1_5.new(rsa)
        return pkcs1_pad.encrypt(data)

except ImportError:
    try:
        import cryptography.hazmat.primitives.ciphers
        import cryptography.hazmat.primitives.ciphers.algorithms
        import cryptography.hazmat.primitives.ciphers.modes
        import cryptography.hazmat.primitives.asymmetric.rsa
        import cryptography.hazmat.primitives.asymmetric.padding
        import cryptography.hazmat.primitives.padding
        import cryptography.hazmat.primitives.serialization

        CRYPTO_BACKEND = "cryptography"

        def aes_encrypt(iv: bytes, key: bytes, data: bytes):
            encryptor = cryptography.hazmat.primitives.ciphers.Cipher(
                cryptography.hazmat.primitives.ciphers.algorithms.AES(key),
                cryptography.hazmat.primitives.ciphers.modes.CBC(iv),
            ).encryptor()
            padder = cryptography.hazmat.primitives.padding.PKCS7(128).padder()
            return b"".join(
                [iv, encryptor.update(padder.update(data)), encryptor.update(padder.finalize()), encryptor.finalize()]
            )

        def load_rsa(key: str):
            return cast(
                cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey,
                cryptography.hazmat.primitives.serialization.load_pem_public_key(key.encode("UTF-8")),
            )

        def rsa_encrypt(rsa: cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey, data: bytes):
            return rsa.encrypt(data, padding=cryptography.hazmat.primitives.asymmetric.padding.PKCS1v15())

    except ImportError:
        raise Exception("Neither 'cryptography' nor 'Pycryptodomex' is installed!")


class SIFResponse:
    def __init__(self, code: int, response: bytes, headers: dict[str, str]):
        self.status_code = code
        self.response = response
        self.headers = headers

    def json(self):
        return json.loads(str(self.response, "UTF-8"))


try:
    import httpx

    HTTP_BACKEND = "httpx"

    class HTTPXSessionWrapper:
        def __init__(self, hostname: str, port: int | None = None):
            self.session = httpx.Client()
            self.url = hostname

    new_http_session = HTTPXSessionWrapper  # type: ignore

    def http_request(  # type: ignore
        session: HTTPXSessionWrapper,
        method: str,
        path: str,
        *,
        data: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ):
        response = session.session.request(method, session.url + path, data=data, headers=headers)
        headers_lower = dict(zip(map(str.lower, response.headers.keys()), response.headers.values()))
        return SIFResponse(response.status_code, response.content, headers_lower)

except ImportError:
    try:
        import requests

        HTTP_BACKEND = "requests"

        class RequestsSessionWrapper:
            def __init__(self, hostname: str, port: int | None = None):
                self.session = requests.Session()
                self.url = hostname

        new_http_session = RequestsSessionWrapper  # type: ignore

        def http_request(  # type: ignore
            session: RequestsSessionWrapper,
            method: str,
            path: str,
            *,
            data: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
        ):
            response = session.session.request(method, session.url + path, data=data, headers=headers)
            headers_lower = dict(zip(map(str.lower, response.headers.keys()), response.headers.values()))
            return SIFResponse(response.status_code, response.content, headers_lower)

    except ImportError:
        import http.client

        HTTP_BACKEND = "http.client"

        def new_http_session(url: str, port: int | None = None):
            if url.startswith("http://"):
                return http.client.HTTPConnection(url[7:], port)
            elif url.startswith("https://"):
                return http.client.HTTPSConnection(url[8:], port)
            else:
                raise ValueError("Unknown scheme")

        def http_request(  # type: ignore
            session: http.client.HTTPSConnection | http.client.HTTPConnection,
            method: str,
            path: str,
            *,
            data: dict[str, str] | None = None,
            headers: dict[str, str] | None = None,
        ):
            new_header = {} if headers is None else headers
            databytes = None
            if data is not None:
                new_header["Content-Type"] = "application/x-www-form-urlencoded"
                databytes = urllib.parse.urlencode(data).encode("UTF-8")
            session.request(
                method,
                path,
                databytes,
                {} if headers is None else headers,
            )
            response = session.getresponse()
            headers_lower = dict(zip(map(str.lower, response.headers.keys()), response.headers.values()))
            return SIFResponse(response.status, response.read(), headers_lower)


def hmac_sha1(message: bytes, key: bytes):
    digest = hmac.new(key, message, hashlib.sha1)
    return digest.digest().hex()


def get_timezone():
    return time.tzname[0]


class SIFException(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class SIFMaintenanceError(SIFException):
    def __init__(self) -> None:
        super().__init__("Maintenance")


class SIFAccountBanned(SIFException):
    def __init__(self) -> None:
        super().__init__("Banned")


class SIFEmu:
    def __init__(
        self,
        binary_key: bytes = b"eit4Ahph4aiX4ohmephuobei6SooX9xo",
        application_id: bytes = b"9c3cf1ac311a8fa1fa9ac2be90dd6067",
    ):
        self.random = secrets.SystemRandom()
        self.client_key = self.random.randbytes(32)
        self.binary_key = binary_key
        self.application_id = application_id
        self.base_xorpad = b""
        self.base_xorpad_dirty = True
        self.platform_type = 1
        self.platform_os = ""
        self.is_jp = False
        self.username = ""
        self.password = ""
        self.counter = 1
        self.user_id = 0
        self.client_version = "58.0"
        self.bundle_version = "9.10"
        self.device_assesment = "eyJIZWxsbyI6ICJXb3JsZCJ9"
        self.auth_token = None
        self.session = new_http_session("https://prod-jp.lovelive.ge.klabgames.net")
        self.debug_last_response = None
        self.debug_last_request = None
        self.rsa = load_rsa(RSA_PUBLIC_KEY)
        self.release_info = {}  # type: dict[int, bytes]
        self.hmac_key = bytes(a ^ b for a, b in zip(binary_key, application_id))
        self.server_version = None

    def reset(self):
        self.random = secrets.SystemRandom()
        self.client_key = self.random.randbytes(32)
        self.base_xorpad_dirty = True
        self.username = ""
        self.password = ""
        self.counter = 1
        self.user_id = 0
        self.auth_token = None
        self.debug_last_response = None
        self.debug_last_request = None
        self.release_info = {}
        self.hmac_key = bytes(a ^ b for a, b in zip(self.binary_key, self.application_id))

    def request_lowlevel(self, endpoint: str, data: dict[str, Any] | list | None = None) -> dict[str, Any]:
        request_data = None
        if data is not None:
            request_data = {"request_data": json.dumps(data)}
        authorize = {
            "consumerKey": "lovelive_test",
            "timeStamp": str(int(time.time())),
            "version": "1.1",
            "nonce": self.counter,
        }
        if self.auth_token:
            authorize["token"] = self.auth_token
        lang = self.get_accept_language()
        headers = {
            "API-Model": "straightforward",
            "Accept-Language": lang[0],
            "Application-ID": "626776655",
            "Authorize": urllib.parse.urlencode(authorize),
            "Bundle-Version": self.bundle_version,
            "Client-Version": self.client_version,
            "Debug": "1",
            "LANG": lang[1],
            "OS": self.get_os(),
            "OS-Version": self.platform_os,
            "Platform-Type": str(self.platform_type),
            "Region": "392",
            "Time-Zone": get_timezone(),
            "X-BUNDLE-ID": self.get_bundle_id(),
        }
        if request_data is not None:
            headers["X-Message-Code"] = hmac_sha1(
                request_data["request_data"].encode("UTF-8"), self.get_client_xorpad()
            )
        if self.user_id > 0:
            headers["User-ID"] = str(self.user_id)
        response = self.debug_request(
            "POST" if data is not None else "GET",
            f"/main.php{endpoint}",
            data=request_data,
            headers=headers,
        )
        self.debug_last_response = response
        if response.headers.get("maintenance", "0") == "1":
            raise SIFMaintenanceError()
        if response.headers.get("version_up", "0") == "1":
            raise SIFException("Need major update")
        if response.status_code == 503:
            raise SIFException("Session expired")
        if response.status_code == 423:
            raise SIFAccountBanned()
        if response.status_code != 200:
            raise SIFException("Unknown error, check debug_last_response")
        jsonresponse = response.json()
        if "release_info" in jsonresponse:
            for keys in jsonresponse["release_info"]:
                self.release_info[keys["id"]] = base64.b64decode(keys["key"])
        if "server-version" in response.headers:
            self.server_version = response.headers["server-version"]
        self.counter = self.counter + 1
        return jsonresponse["response_data"]

    def request(self, *requests: "SIFEmuRequest"):
        ts = int(time.time())
        if len(requests) == 1:
            req = requests[0]
            req.add_more_context(self)
            req_mod = req.get_module_name()
            req_act = req.get_action_name()
            req_def = {"module": req_mod, "action": req_act, "timeStamp": ts}
            return self.request_lowlevel(f"/{req_mod}/{req_act}", req.get_data() | req_def)
        else:
            req_all = []
            for req in requests:
                req.add_more_context(self)
                req_mod = req.get_module_name()
                req_act = req.get_action_name()
                req_all.append(req.get_data() | {"module": req_mod, "action": req_act, "timeStamp": ts})
            return self.request_lowlevel("/api", req_all)

    def debug_request(self, method: str, url: str, data: dict[str, str] | None, headers: dict[str, str]):
        self.debug_last_request = {"method": method, "url": url, "data": data, "headers": headers}
        # return self.session.request(method, url, data=data, headers=headers)
        return http_request(self.session, method, url, data=data, headers=headers)

    def uuid(self):
        return str(uuid.uuid4()).upper()

    def get_client_xorpad(self):
        if self.base_xorpad_dirty:
            self.base_xorpad = bytes(a ^ b for a, b in zip(self.hmac_key, self.client_key))
            self.base_xorpad_dirty = False
        return self.base_xorpad

    def set_client_version(self, version: str):
        self.client_version = version

    def get_client_version(self):
        return self.client_version

    def get_bundle_id(self):
        if self.platform_type == 1:
            return "jp.klab.lovelive" if self.is_jp else "jp.klab.lovelive-en"
        elif self.platform_type == 2:
            return "klb.android.lovelive" if self.is_jp else "klb.android.lovelive_en"
        else:
            raise NotImplementedError("Don't use SIF-Win32!")

    def get_accept_language(self):
        return ("ja-jp", "ja") if self.is_jp else ("en-us", "en")

    def get_os(self):
        if self.platform_type == 1:
            return "iOS"
        elif self.platform_type == 2:
            return "Android"
        elif self.platform_type == 3:
            return "Win32"  # Don't!
        else:
            raise Exception("Unknown Platform-Type")

    def get_release_info(self):
        return self.release_info

    def set_bundle_version(self, bundle: str):
        self.bundle_version = bundle

    def set_os_ios(self, type: str):
        self.platform_type = 1
        self.platform_os = type

    def set_os_android(self, type: str):
        self.platform_type = 2
        self.platform_os = type

    def set_os_win32(self, type: str):
        raise NotImplementedError("Don't!")

    def set_device_assesment(self, dev: str):
        self.device_assesment = dev

    def set_sif_jp(self):
        self.is_jp = True

    def set_sif_ww(self):
        self.is_jp = False

    def set_username(self, username: str):
        self.username = username

    def set_password(self, password: str):
        self.password = password

    def generate_credentials(self):
        self.username = self.uuid()
        self.password = self.random.randbytes(64).hex()

    def get_encrypted_credentials(self):
        key = self.get_client_xorpad()[:16]
        iv = self.random.randbytes(16)
        e_username = aes_encrypt(iv, key, self.username.encode("UTF-8"))
        e_password = aes_encrypt(iv, key, self.password.encode("UTF-8"))
        return (str(base64.b64encode(e_username), "UTF-8"), str(base64.b64encode(e_password), "UTF-8"))

    def r_login_authkey(self) -> tuple[str, bytes]:
        iv = self.random.randbytes(16)
        auth_data_plain = json.dumps({"1": self.username, "2": self.password, "3": self.device_assesment})
        dummy_token = base64.b64encode(rsa_encrypt(self.rsa, self.client_key))
        auth_data = base64.b64encode(aes_encrypt(iv, self.client_key[:16], auth_data_plain.encode("UTF-8")))
        response = self.request_lowlevel(
            "/login/authkey", {"dummy_token": str(dummy_token, "UTF-8"), "auth_data": str(auth_data, "UTF-8")}
        )
        return (response["authorize_token"], base64.b64decode(response["dummy_token"]))

    def initial_token(self):
        self.auth_token, self.hmac_key = self.r_login_authkey()
        self.base_xorpad_dirty = True

    def r_login_startup(self):
        username, password = self.get_encrypted_credentials()
        return self.request_lowlevel("/login/startUp", {"login_key": username, "login_passwd": password})

    def r_login_login(self):
        username, password = self.get_encrypted_credentials()
        if self.platform_type == 1:
            devtoken = self.uuid()
        else:
            devtoken = self.random.randbytes(64).hex(":").upper()
        return self.request_lowlevel(
            "/login/login",
            {"login_key": username, "login_passwd": password, "devtoken": devtoken},
        )

    def startup(self):
        self.r_login_startup()
        return (self.username, self.password)

    def login(self):
        response = self.r_login_login()
        if "error_code" in response:
            if response["error_code"] == 607:
                raise SIFException("Invalid username and password")
            raise SIFException("Unknown login error")
        self.user_id = cast(int, response["user_id"])
        self.auth_token = cast(str, response["authorize_token"])

    def is_need_update(self):
        return self.server_version is not None and self.server_version != self.client_version

    def get_server_version(self):
        return self.server_version


class SIFEmuRequest:
    """
    SIFEmu request object. Calling order by SIFEmu are:
    1. add_more_context
    2. use_custom_xmc
    3. get_data
    """

    def __init__(self, module: str, action: str, custom_xmc: bool = False):
        self.module = module
        self.action = action
        self.custom_xmc_calc = custom_xmc

    def get_module_name(self):
        return self.module

    def get_action_name(self):
        return self.action

    def get_data(self):
        return {}

    def use_custom_xmc(self):
        return self.custom_xmc_calc

    def add_more_context(self, sifemu: SIFEmu):
        pass
