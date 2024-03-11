import pytest
from censoror import Censor

def test_censor_phone_simple():
    censor = Censor(".", ".")
    content = "Call me at 123-456-7890."
    expected = "Call me at ************."
    result, count = censor._censor_phones(content)
    assert result == expected
    assert count == 1


