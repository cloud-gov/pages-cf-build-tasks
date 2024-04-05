import os
import pytest
from common.lib.utils import run

base = os.path.dirname(__file__)
happy_script = os.path.join(base, 'scripts', 'succeed.sh')
sad_script = os.path.join(base, 'scripts', 'fail.sh')


def test_happy_path():
    output = run(['bash', happy_script])
    assert output.returncode == 0
    assert output.stdout is None


def test_happy_path_output():
    output = run(['bash', happy_script], capture_output=True)
    assert output.returncode == 0
    assert output.stdout.strip() == "happy message"


def test_sad_path():
    with pytest.raises(Exception) as einfo:
        run(['bash', sad_script])

    assert str(einfo.value) == 'Error running subprocess'


def test_sad_path_output():
    with pytest.raises(Exception) as einfo:
        run(['bash', sad_script], capture_output=True)

    assert str(einfo.value).strip() == 'error message'
