import pytest

from common.validation import is_finite_number, is_integer


@pytest.mark.parametrize('value', [0, -1, 42])
def test_is_integer_accepts_integers(value):
    assert is_integer(value)


@pytest.mark.parametrize('value', [True, False, 1.0, 1.5, '1', None])
def test_is_integer_rejects_other_values(value):
    assert not is_integer(value)


@pytest.mark.parametrize('value', [0, -1, 1.5, 42])
def test_is_finite_number_accepts_finite_numbers(value):
    assert is_finite_number(value)


@pytest.mark.parametrize(
    'value',
    [
        True,
        False,
        float('nan'),
        float('inf'),
        -float('inf'),
        '1',
        None,
    ],
)
def test_is_finite_number_rejects_invalid_values(value):
    assert not is_finite_number(value)