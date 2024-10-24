import hashlib
import os
import random
import re
import string
from base64 import urlsafe_b64decode
from urllib.parse import urlparse

from bidict import bidict
from cryptography.fernet import Fernet


def _generate_random_ascii_string(length: int = 30) -> str:
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


def _split_interval_string(s: str) -> tuple[int, str]:
    for i, char in enumerate(s):
        if not char.isdigit():
            return int(s[:i]), s[i:]
    return int(s), ""


def _extract_uri_scheme(path: str) -> str:
    result = urlparse(path)
    return result.scheme


def _make_python_identifier(str_: str) -> str:
    return re.sub(r"\W|^(?=\d)", "_", str_)


def _create_reproducible_hash(input_string: str) -> str:
    # Encode the input string
    encoded_string = input_string.encode()

    # Create a SHA-32 hash object
    sha256_hash = hashlib.md5()

    # Update the hash object with the bytes-like object (encoded string)
    sha256_hash.update(encoded_string)

    # Generate the hexadecimal representation of the digest
    hex_digest = sha256_hash.hexdigest()

    return hex_digest


def _replace_with_dict(
    text: str, replace_dict: dict[str, str] | bidict[str, str]
) -> str:
    for k, v in replace_dict.items():
        text = text.replace(k, v)
    return text


def _escape_triple_quotes(text):
    if text is None:
        return None
    if "'''" in text:
        text = text.replace("'''", "\\'\\'\\'")
    if '"""' in text:
        text = text.replace('"""', '\\"\\"\\"')
    return text


def decrypt_secret(secret: str) -> str:
    cipher = Fernet(os.getenv("ENCRYPTION_KEY"))

    decrypted_secret = cipher.decrypt(urlsafe_b64decode(secret)).decode("utf-8")
    return decrypted_secret


# NOTE: Starting in Ibis 10.0, Ibis now uses nomenclature for tables (i.e. catalog, database, name), that is distinct from how we usually think about it. Database, schema, name. Until we rename our variables, the variable naming will be confusing.
