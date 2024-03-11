import pytest
from censoror import Censor

def test_censor_simple_address():
    censor = Censor(".", ".")
    content = "My address is 7000 SW Nook St, 45688."
    expected = "My address is ************, *****."
    result, count = censor._censor_addresses(content)
    assert result == expected, f"Expected: {expected}, but got: {result}"
    assert count == 1, "Expected 1 address to be censored"
