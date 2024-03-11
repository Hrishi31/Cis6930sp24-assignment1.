import pytest
from censoror import Censor

def test_censor_simple_date():
    censor = Censor(".", ".")
    content = "The event is on 01/23/2024."
    expected = "The event is on **********."
    result, count = censor._censor_dates(content)
    assert result == expected
    assert count == 1


