from unittest.mock import MagicMock, patch

import pytest

import data.db_connect as dbc

COLLECTION = 'test_collection'


def make_fake_client():
    """A client whose collections are empty."""
    fake_client = MagicMock()
    fake_collection = fake_client[dbc.SE_DB][COLLECTION]
    fake_collection.find.return_value = []
    return fake_client


@patch('data.db_connect.connect_db', autospec=True)
def test_needs_db_connects_before_calling(mock_connect):
    calls = []
    mock_connect.side_effect = lambda: calls.append('connect')

    @dbc.needs_db
    def fetch(value):
        calls.append('fetch')
        return value

    assert fetch('result') == 'result'
    assert calls == ['connect', 'fetch']


def test_needs_db_keeps_function_name_and_docstring():
    assert dbc.read.__name__ == 'read'
    assert 'list from the db' in dbc.read.__doc__


DB_CALLS = [
    (dbc.create, (COLLECTION, {'id': 'x'})),
    (dbc.read_one, (COLLECTION, {'id': 'x'})),
    (dbc.delete, (COLLECTION, {'id': 'x'})),
    (dbc.delete_many, (COLLECTION,)),
    (dbc.update, (COLLECTION, {'id': 'x'}, {'name': 'y'})),
    (dbc.read, (COLLECTION,)),
    (dbc.read_dict, (COLLECTION, 'id')),
    (dbc.fetch_all_as_dict, ('id', COLLECTION)),
]


@pytest.mark.parametrize('func, args', DB_CALLS)
def test_db_call_connects_when_there_is_no_client(func, args):
    fake_client = make_fake_client()

    def fake_connect():
        dbc.client = fake_client

    with patch.object(dbc, 'client', None), \
            patch('data.db_connect.connect_db', side_effect=fake_connect) \
            as mock_connect:
        func(*args)
    mock_connect.assert_called_once()
