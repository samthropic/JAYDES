# Database schema and local setup

Application data belongs in MongoDB database `seDB`. All reads and writes go through `data/db_connect.py`. States and regions are still Python dictionaries in `states/query.py` and `regions/query.py`. Those modules do not call `data/db_connect.py` yet.

## Collections

One collection per resource. State and region ids are 2-letter codes. Neighborhood and property ids are non-empty strings. A parent field stores the parent's `id`.

### `states`

Present today as `STATE_TEST_DATA` in `states/query.py`.

| Field | Required | Notes |
|-------|----------|--------|
| `id` | yes | 2-letter code, such as `NY`. This is the abbreviation. There is no separate abbreviation field. |
| `name` | yes | State name |
| `capital` | yes | |
| `population` | yes | Non-negative integer |
| `area_sq_miles` | yes | Number |
| `region_id` | planned | Id of an existing region, such as `NE`. Not stored yet. |

### `regions`

Present today as `REGION_TEST_DATA` in `regions/query.py`. A region is a multi-state area (Northeast, Southeast, Midwest), not a city.

| Field | Required | Notes |
|-------|----------|--------|
| `id` | yes | 2-letter code, such as `NE`. Today this is the dictionary key, not a field on the record. |
| `name` | yes | |
| `population` | yes | Non-negative integer |
| `description` | yes | |

### `neighborhoods`

Not in the repository yet. Jacob adds this collection.

| Field | Required | Notes |
|-------|----------|--------|
| `id` | yes | Non-empty string |
| `name` | yes | |
| `state_id` | yes | `id` of an existing state |

### `properties`

Not in the repository yet. Danny adds this collection.

| Field | Required | Notes |
|-------|----------|--------|
| `id` | yes | Non-empty string |
| `address` | yes | |
| `neighborhood_id` | yes | `id` of an existing neighborhood |
| `price` | yes | Non-negative number |
| `bedrooms` | yes | Non-negative number |
| `bathrooms` | yes | Non-negative number |
| `latitude` | yes | |
| `longitude` | yes | |

## Relationships

```
regions 1──* states 1──* neighborhoods 1──* properties
```

- A state's `region_id` must match an existing region `id`, once that field is added.
- A neighborhood's `state_id` must match an existing state `id`.
- A property's `neighborhood_id` must match an existing neighborhood `id`.

Current sample ids are `AL`, `AK`, and `AZ` for states, and `NE`, `SE`, and `MW` for regions. New mock records should use those ids until more states are loaded.

## Local development

From the repository root:

```bash
make dev_env
export PYTHONPATH="$(pwd)"
```

`make dev_env` installs `requirements-dev.txt`, including `pymongo`. `PYTHONPATH` must be the repository root so imports such as `data.db_connect` and `states.query` resolve.

MongoDB listens on `localhost:27017`. Leave `CLOUD_MONGO` unset, or set it to `0`. `common.mk` exports `CLOUD_MONGO=0` when tests run. `connect_db()` then uses a local client, and the database name is `seDB`.

`CLOUD_MONGO=1` connects to Atlas and requires `MONGO_PASSWD`. The connection string in `data/db_connect.py` still uses the course Atlas account. Use local MongoDB until that URI is replaced.

`is_db_up()` in `data/db_connect.py` always returns true. It does not ping the server.

## Running tests

From the repository root, after the local setup above:

```bash
make dev_env
export PYTHONPATH="$(pwd)"
make all_tests
```

`make all_tests` lints and runs pytest for `server`, `states`, and `regions`. `common.mk` sets `CLOUD_MONGO=0` for those runs. GitHub Actions runs the same `make all_tests` target on push and pull request to `main` (`.github/workflows/main.yml`). The PythonAnywhere deploy step in that workflow stays commented out.

## Seeding

No seed script exists yet. The first load should copy the mock data the API already uses.

| Collection | Source | What to load |
|------------|--------|----------------|
| `states` | `STATE_TEST_DATA` in `states/query.py` | `AL`, `AK`, `AZ`, including `name`, `capital`, `population`, and `area_sq_miles`. The dictionary key becomes `id`. |
| `regions` | `REGION_TEST_DATA` in `regions/query.py` | `NE`, `SE`, `MW`, including `name`, `population`, and `description`. The dictionary key becomes `id`. |
| `states` (optional fuller list) | `states/raw_data/states.csv` | Columns `Abbrev`, `Latitude`, `Longitude`, `State`. `states/load.py` only prints these rows. It does not insert them. Coordinates are not fields on the state record yet. |
| `neighborhoods` | `neighborhoods/query.py`, when it exists | At least five neighborhoods whose `state_id` is `AL`, `AK`, or `AZ`. |
| `properties` | `properties/query.py`, when it exists | At least five properties whose `neighborhood_id` matches a neighborhood. |

`data/bkup/games.json` and `data/bkup/users.json` are backups of the old `gamesDB` database. They are not seed data for this API. Do not import them into `seDB`.
