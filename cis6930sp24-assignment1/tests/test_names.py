import pytest
from censoror import Censor

def test_censor_single_name():
    censor = Censor(".", ".")
    content = "Hello, my name is John Doe."
   
    expected = "Hello, my name is ********."
    result, count = censor._censor_names(content)
    assert result == expected
    assert count == 1

def test_censor_multiple_names():
    censor = Censor(".", ".")
    content = "Sarah and Mike went to visit John."
    expected = "***** and **** went to visit ****."
    result, count = censor._censor_names(content)
    assert result == expected
    assert count == 3


