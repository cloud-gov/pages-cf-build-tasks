import os
import subprocess
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def encrypt(value, key):
    m = hashlib.sha256()
    m.update(key.encode())
    hashed_key = m.digest()

    iv = os.urandom(16)

    encryptor = Cipher(
        algorithms.AES(hashed_key),
        modes.GCM(iv),
    ).encryptor()

    ciphertext = encryptor.update(value.encode()) + encryptor.finalize()

    return ":".join([encryptor.tag.hex(), iv.hex(), ciphertext.hex()])


def decrypt(ciphertext, key):
    m = hashlib.sha256()
    m.update(key.encode())
    hashed_key = m.digest()

    auth_tag, iv, encrypted = [bytes.fromhex(hex) for hex in ciphertext.split(":")]

    decryptor = Cipher(
        algorithms.AES(hashed_key), modes.GCM(iv, auth_tag), backend=default_backend()
    ).decryptor()

    return (decryptor.update(encrypted) + decryptor.finalize()).decode()


def decrypt_dict_values(encrypted_dict, key):
    decrypted = {}

    for k, v in encrypted_dict.items():
        decrypted[k] = decrypt(v, key)

    return decrypted


def run(*args, **kwargs):
    # always run with text output for easier error reporting
    kwargs["text"] = True
    output = subprocess.run(*args, **kwargs)
    if output.returncode > 0:
        if output.stderr:
            raise Exception(output.stderr)
        else:
            raise Exception("Error running subprocess")

    return output
