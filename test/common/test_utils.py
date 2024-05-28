import os
import pytest
from common.lib.utils import encrypt, decrypt, decrypt_dict_values, run

base = os.path.dirname(__file__)
happy_script = os.path.join(base, "scripts", "succeed.sh")
sad_script = os.path.join(base, "scripts", "fail.sh")


def test_happy_path():
    output = run(["bash", happy_script])
    assert output.returncode == 0
    assert output.stdout is None


def test_happy_path_output():
    output = run(["bash", happy_script], capture_output=True)
    assert output.returncode == 0
    assert output.stdout.strip() == "happy message"


def test_sad_path():
    with pytest.raises(Exception) as einfo:
        run(["bash", sad_script])

    assert str(einfo.value) == "Error running subprocess"


def test_sad_path_output():
    with pytest.raises(Exception) as einfo:
        run(["bash", sad_script], capture_output=True)

    assert str(einfo.value).strip() == "error message"


def test_decrypt():
    ciphertext = (
        "6a7495108a7f8c9ab4d0990854240242:"
        "e05f0d25446be83fa92aa9586610496b:"
        "560d3e8ff02f852104417a"
    )
    key = "shhhhhhh"

    expected = "hello world"

    result = decrypt(ciphertext, key)

    assert result == expected


def test_decrypt_dict_values():
    key = "shhhhhhh"
    dict_key_1 = "name"
    value_1 = "world"
    value_1_enc = encrypt(value_1, key)
    dict_key_2 = "other"
    value_2 = "this-was-encrypted"
    value_2_enc = encrypt(value_2, key)
    encrypted_dict = dict({dict_key_1: value_1_enc, dict_key_2: value_2_enc})

    result = decrypt_dict_values(encrypted_dict, key)

    for k in result.keys():
        assert k == dict_key_1 or k == dict_key_2

    assert result[dict_key_1] == value_1
    assert result[dict_key_2] == value_2


def test_encrypting():
    value = "hello world"
    key = "shhhhhhh"
    enc = encrypt(value, key)
    result = decrypt(enc, key)

    assert result == value
