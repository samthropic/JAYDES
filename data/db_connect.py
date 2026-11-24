"""
All interaction with MongoDB should be through this file!
We may be required to use a new database at any point.
"""
import functools
import os

import pymongo as pm

LOCAL = "0"
CLOUD = "1"

SE_DB = 'seDB'
SERVER_SELECTION_TIMEOUT_MS = 2000

DEFAULT_CLOUD_USER = 'sf4095'
DEFAULT_CLOUD_HOST = 'test.3jsm0.mongodb.net'
CLOUD_MONGO_OPTIONS = 'retryWrites=true&w=majority'

client = None

AUTH_FAILED_CODES = (13, 18, 8000)
MONGO_ID = '_id'


def connect_db():
    """
    This provides a uniform way to connect to the DB across all uses.
    Returns a mongo client object... maybe we shouldn't?
    Also set global client variable.
    We should probably either return a client OR set a
    client global.
    """
    global client
    if client is None:  # not connected yet!
        print('Setting client because it is None.')
        if os.environ.get('CLOUD_MONGO', LOCAL) == CLOUD:
            user = os.environ.get('MONGO_USER', DEFAULT_CLOUD_USER)
            host = os.environ.get('MONGO_HOST', DEFAULT_CLOUD_HOST)
            password = os.environ.get('MONGO_PASSWD')
            if not password:
                raise ValueError('You must set your password '
                                 + 'to use Mongo in the cloud.')
            print('Connecting to Mongo in the cloud.')
            client = pm.MongoClient(
                f'mongodb+srv://{user}:{password}'
                + f'@{host}/?{CLOUD_MONGO_OPTIONS}',
                serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
            )
        else:
            print("Connecting to Mongo locally.")
            client = pm.MongoClient(
                serverSelectionTimeoutMS=SERVER_SELECTION_TIMEOUT_MS,
            )
    return client


def needs_db(func):
    """
    Decorator for functions that use the global client. It makes sure the
    client exists before the function runs, so callers never have to
    remember to call connect_db() first.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        connect_db()
        return func(*args, **kwargs)
    return wrapper


def is_db_up():
    """
    Return True when MongoDB accepts a ping.
    """
    try:
        connect_db().admin.command('ping')
    except pm.errors.ServerSelectionTimeoutError as e:
        print(
            'Could not reach Mongo (check Atlas IP access list, '
            f'DNS, TLS, or VPN): {e}'
        )
        return False
    except pm.errors.OperationFailure as e:
        if e.code in AUTH_FAILED_CODES:
            print(
                'Mongo is reachable, but authentication failed '
                f'(code {e.code}): {e.details}'
            )
        else:
            print(f'Mongo operation failed (code {e.code}): {e}')
        return False
    except pm.errors.ConfigurationError as e:
        print(
            'Invalid Mongo configuration '
            f'(bad URI or DNS/SRV lookup): {e}'
        )
        return False
    except (pm.errors.PyMongoError, ValueError, OSError) as e:
        print(
            'Unexpected error connecting to Mongo: '
            f'{type(e).__name__}: {e}'
        )
        return False
    return True


def convert_mongo_id(doc: dict):
    if MONGO_ID in doc:
        # Convert mongo ID to a string so it works as JSON
        doc[MONGO_ID] = str(doc[MONGO_ID])


@needs_db
def ensure_unique_index(collection, field, db=SE_DB):
    """Ensure MongoDB enforces uniqueness for a field, including direct writes."""
    return client[db][collection].create_index(field, unique=True)


@needs_db
def create(collection, doc, db=SE_DB):
    """
    Insert a single doc into collection.
    """
    print(f'{db=}')
    return client[db][collection].insert_one(doc)


@needs_db
def read_one(collection, filt, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    Return None if not found.
    """
    for doc in client[db][collection].find(filt):
        convert_mongo_id(doc)
        return doc


@needs_db
def delete(collection: str, filt: dict, db=SE_DB):
    """
    Find with a filter and return on the first doc found.
    """
    print(f'{filt=}')
    del_result = client[db][collection].delete_one(filt)
    return del_result.deleted_count


@needs_db
def delete_many(collection, filt=None, db=SE_DB):
    """
    Delete every document matching filt. An empty filt clears the collection.
    """
    if filt is None:
        filt = {}
    del_result = client[db][collection].delete_many(filt)
    return del_result.deleted_count


@needs_db
def update(collection, filters, update_dict, db=SE_DB):
    return client[db][collection].update_one(filters, {'$set': update_dict})


@needs_db
def read(collection, db=SE_DB, no_id=True, filt=None) -> list:
    """
    Returns a list from the db.
    """
    if filt is None:
        filt = {}
    ret = []
    for doc in client[db][collection].find(filt):
        if no_id:
            del doc[MONGO_ID]
        else:
            convert_mongo_id(doc)
        ret.append(doc)
    return ret


def read_dict(collection, key, db=SE_DB, no_id=True) -> dict:
    recs = read(collection, db=db, no_id=no_id)
    recs_as_dict = {}
    for rec in recs:
        recs_as_dict[rec[key]] = rec
    return recs_as_dict


@needs_db
def fetch_all_as_dict(key, collection, db=SE_DB):
    ret = {}
    for doc in client[db][collection].find():
        del doc[MONGO_ID]
        ret[doc[key]] = doc
    return ret
