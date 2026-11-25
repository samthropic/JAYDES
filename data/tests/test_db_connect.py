from unittest.mock import MagicMock, patch

import pytest

import data.db_connect as dbc

COLLECTION = 'test_collection'


def test_log_mongo_config_warns_when_cloud_password_missing(capsys):
    with patch.dict('os.environ', {'CLOUD_MONGO': '1'}, clear=False):
        import os
        os.environ.pop('MONGO_PASSWD', None)
        dbc.log_mongo_config()
        out = capsys.readouterr().out
    assert 'WARNING' in out
    assert 'MONGO_PASSWD' in out


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
    (dbc.ensure_unique_index, (COLLECTION, 'id')),
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


@pytest.mark.parametrize('database', [dbc.SE_DB, 'custom_database'])
def test_unique_index_connects_before_creating_index(database):
    fake_client = make_fake_client()
    collection = fake_client[database][COLLECTION]
    calls = []

    def connect():
        calls.append('connect')
        dbc.client = fake_client

    def create_index(field, unique):
        calls.append('create_index')
        assert dbc.client is fake_client
        assert field == 'id'
        assert unique is True
        return 'id_1'

    collection.create_index.side_effect = create_index
    with patch.object(dbc, 'client', None), \
            patch.object(dbc, 'connect_db', side_effect=connect) \
            as mock_connect:
        result = dbc.ensure_unique_index(COLLECTION, 'id', db=database)

    assert result == 'id_1'
    assert calls == ['connect', 'create_index']
    mock_connect.assert_called_once_with()
    collection.create_index.assert_called_once_with('id', unique=True)
