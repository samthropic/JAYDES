# Geographic Real Estate API — Project Plan

## Project Overview

Our goal is to build a RESTful API server for geographic real estate data on the Flask app already in this repository.

The API will support CRUD (Create, Read, Update, Delete) operations on geographic and housing data.

The running app is `server/endpoints.py` (Flask and flask-restx). States live in `states/`. Regions live in `regions/`. Shared MongoDB helpers live in `data/db_connect.py`. Tests run through the package makefiles and `make all_tests`.

### Data Hierarchy

The repository already models multi-state regions and US states. It does not model a city as a region. New housing data hangs off the state, which is the resource that already exists.

Region → State → Neighborhood → Property

Example:
- Region: Northeast (`NE`)
- State: New York (`NY`)
- Neighborhood: Chelsea
- Property: 123 W 20th St, Apartment 4B

States and regions currently use in-memory dictionaries in `states/query.py` and `regions/query.py`. `data/db_connect.py` can talk to MongoDB database `seDB`, and the query modules do not call it yet. `states/raw_data/states.csv` is a separate state file (abbreviation, latitude, longitude, name) loaded only by `states/load.py`, which prints rows and does not seed the API.

`security/`, `examples/`, `data/manus/`, `data/bkup/` (`games` and `users`), and `.travis.yml` are leftover from the original demo. They are out of scope. Do not build features on them.

We will keep the current mock dictionaries, then move reads and writes into `seDB`, and add search, caching, testing, and cloud deployment.

## Project Requirements

- [ ] Implement CRUD operations for all major resources
- [ ] Create at least 12 API endpoints
- [ ] Store data in MongoDB database `seDB` through `data/db_connect.py`
- [ ] Write unit tests for every endpoint and other functions
- [ ] Document endpoints using the existing flask-restx Swagger UI (`/swagger.json`)
- [ ] Implement in-memory caching where practical
- [ ] Update CI so tests run on `main`, and add a deployment job
- [ ] Deploy the API server to the cloud, replacing the PythonAnywhere demo scripts

---

## 1. Team Responsibilities

Each member will own a primary feature or area of the project.

### Ishraq — States API & Integration
- Implement CRUD operations for states in `states/query.py` and `server/endpoints.py`
- Define shared API conventions from the endpoints that already exist
- Add `region_id` on states and coordinate that link with Yasmin
- Write tests and Swagger documentation for state endpoints
- Review and integrate team pull requests

### Yasmin — Regions API
- Implement CRUD operations for regions in `regions/query.py` and `server/endpoints.py`
- Keep regions as multi-state areas (`NE`, `SE`, `MW`), matching the current mock data
- Make region reads return a list of records with `id`, matching states
- Validate region data and the state-to-region link
- Write tests and Swagger documentation for region endpoints

### Jacob — Neighborhoods API
- Add a `neighborhoods/` package that follows `states/` and `regions/`
- Implement CRUD operations for neighborhoods
- Establish relationships between neighborhoods and states (`state_id`)
- Implement neighborhood lookup functionality
- Write tests and Swagger documentation for neighborhood endpoints

### Danny — Properties API
- Add a `properties/` package that follows `states/` and `regions/`
- Implement CRUD operations for properties
- Define property attributes (price, bedrooms, bathrooms, and so on)
- Implement property search and filtering
- Write tests and Swagger documentation for property endpoints

### Sam — Database & Infrastructure
- Finish database connectivity in `data/db_connect.py` and switch states and regions from dictionaries to `seDB` when the team is ready
- Seed from `STATE_TEST_DATA`, `REGION_TEST_DATA`, and `states/raw_data/states.csv`
- Update the existing GitHub Actions workflow and the root makefile
- Configure shared testing infrastructure
- Implement caching utilities
- Replace the PythonAnywhere demo deploy with the team's cloud deployment

**Note:** Every member is responsible for testing and documenting their own features. Sam handles shared infrastructure, not everyone's tests.

---

## 2. Data Models

States and regions already exist as Python dictionaries. Neighborhoods and properties are new. Parent links below that are marked planned are not in the dictionaries yet.

IDs already in the repo are 2-letter codes. Neighborhood and property ids are strings. A parent id stores the parent's `id`.

### State (exists: `states/query.py`)

Current fields:
- id — 2-letter code, such as `NY` (constant `states.query.ID`)
- name
- capital
- population
- area_sq_miles

Planned field:
- region_id — id of an existing region, such as `NE`

`GET /states` returns:

```json
{ "States:": [ { "id": "AL", "name": "Alabama", "capital": "Montgomery", "population": 4903185, "area_sq_miles": 52420 } ] }
```

There is no separate `abbreviation` field. The code is `id`.

### Region (exists: `regions/query.py`)

Current fields, stored as a dict keyed by code:
- id — 2-letter code, such as `NE` (today this is the dict key, not a field on the record)
- name
- population
- description

`GET /regions` currently returns a dict, not a list:

```json
{ "Regions:": { "NE": { "name": "Northeast", "population": 55000000, "description": "Northeastern United States" } } }
```

Yasmin will change `regions.query.read()` so this becomes a list of objects with `id`, under the same `"Regions:"` key, matching states.

Regions do not have `state_id`. A region is not a city.

### Neighborhood (new: `neighborhoods/`)

- id
- name
- state_id

### Property (new: `properties/`)

- id
- address
- neighborhood_id
- price
- bedrooms
- bathrooms
- latitude
- longitude

### Data Conventions
- State and region ids are 2-letter strings. Neighborhood and property ids are non-empty strings.
- Every state must reference an existing region through `region_id` once that field is added.
- Every neighborhood must reference an existing state through `state_id`.
- Every property must reference an existing neighborhood through `neighborhood_id`.
- All required fields should be validated.
- Mock data should use the same ids the query modules already use (`AL`, `AK`, `AZ`, `NE`, `SE`, `MW`) before new records are added.
- List endpoints wrap the collection in a labeled object (`"States:"`, `"Regions:"`). They do not return a bare array.
- When `is_db_up()` is false, list endpoints respond with HTTP 503. Today that function always returns true and does not ping MongoDB.

### Database
- Application database name: `seDB` (`data/db_connect.py`).
- Local connection: `CLOUD_MONGO` unset or `0`, MongoDB on `localhost:27017`. `common.mk` exports `CLOUD_MONGO=0` for tests.
- Cloud connection: `CLOUD_MONGO=1` and `MONGO_PASSWD` set. The current URI still points at the course Atlas account and must be replaced before the team uses it.
- `data/common.sh` and `data/bkup/` refer to `gamesDB`. That is not this API's database.

---

## 3. Week 1 — Project Foundation

**Deadline: October 8, 2026**

### Goal

Lock the models to the code already in the repo, document sample data, and make the existing test workflow reliable.

Each member must complete **2 meaningful commits**.

### Ishraq — States & API Architecture

**Commit 1: Define API Structure**
- [ ] Create `docs/api-design.md`
- [ ] Document states, regions, neighborhoods, and properties using the hierarchy in this plan
- [ ] Document the existing routes: `GET /hello`, `GET /endpoints`, `GET /states`, `GET /regions`
- [ ] Document the `"States:"` / `"Regions:"` response envelopes and the 503 behavior

Commit message:
`docs: define real estate API architecture`

**Commit 2: Lock the States Endpoint**
- [ ] `GET /states` already reads `STATE_TEST_DATA`. Keep that behavior.
- [ ] Assert the fields the handler actually returns: `id`, `name`, `capital`, `population`, `area_sq_miles`
- [ ] Keep the Swagger `State` model in `server/endpoints.py` aligned with those fields

Commit message:
`test: cover existing states endpoint contract`

### Yasmin — State and Region Data

**Commit 1: Record Existing Region Data**
- [ ] Treat `REGION_TEST_DATA` in `regions/query.py` as the region seed (`NE`, `SE`, `MW`)
- [ ] Document each region's `name`, `population`, and `description`
- [ ] Do not add a `state_id` field. Regions are not children of states.

Commit message:
`docs: describe existing region mock data`

**Commit 2: Region Read Shape and Validation**
- [ ] Change `regions.query.read()` to return a list of `{id, name, population, description}`
- [ ] Point `GET /regions` at that list, still under `"Regions:"`
- [ ] Keep validation for the 2-letter code, non-empty name, and non-negative population
- [ ] Update `regions/tests/test_query.py` and `server/tests/test_endpoints.py` for the list shape

Commit message:
`feat: return regions as a list of records`

### Jacob — Neighborhood Data

**Commit 1: Add Neighborhood Mock Data**
- [ ] Create `neighborhoods/query.py` with at least 5 sample neighborhoods
- [ ] Include `state_id` for each neighborhood, using a state id that exists in `STATE_TEST_DATA` (`AL`, `AK`, or `AZ`)
- [ ] Follow the state module layout: query module plus `neighborhoods/tests/`

Commit message:
`feat: add neighborhood mock data`

**Commit 2: Neighborhood Validation**
- [ ] Validate required neighborhood fields
- [ ] Verify each `state_id` refers to an existing state
- [ ] Write unit tests for validation functions

Commit message:
`test: add neighborhood data validation tests`

### Danny — Property Data

**Commit 1: Add Property Mock Data**
- [ ] Create `properties/query.py` with at least 5 sample properties
- [ ] Include address, price, bedrooms, and bathrooms
- [ ] Add geographic coordinates
- [ ] Associate properties with neighborhoods through `neighborhood_id`

Commit message:
`feat: add mock real estate property data`

**Commit 2: Property Validation**
- [ ] Validate required property fields
- [ ] Validate price and numeric attributes
- [ ] Write unit tests for property validation

Commit message:
`test: add property data validation tests`

### Sam — Database & Infrastructure

**Commit 1: Database Planning**
- [ ] Document the schema in this plan's data-model section as the database schema: current state and region fields, planned `region_id`, and the new neighborhood and property collections
- [ ] Document local setup: `make dev_env`, `PYTHONPATH` set to the repo root, local MongoDB, `CLOUD_MONGO=0`, database `seDB`
- [ ] Outline seeding from `STATE_TEST_DATA`, `REGION_TEST_DATA`, and `states/raw_data/states.csv`
- [ ] State that `data/bkup/games.json` and `data/bkup/users.json` are not seed data

Commit message:
`docs: define database schema and setup`

**Commit 2: Testing Infrastructure**
- [ ] The workflow already exists at `.github/workflows/main.yml` and runs on push and pull request to `main`
- [ ] Include `regions` tests in `make all_tests` (today the root makefile runs `server` and `states` only)
- [ ] Remove the `pa_deploy` environment requirement so tests are not blocked on the old PythonAnywhere environment
- [ ] Leave the PythonAnywhere deploy step commented until week 5
- [ ] Run `make all_tests` and document the local commands in the database setup doc

Commit message:
`ci: configure automated testing workflow`

### Week 1 Completion Checklist

- [ ] All 5 members have made 2 commits each
- [ ] Data models match `states/query.py` and `regions/query.py`, with neighborhoods and properties specified
- [ ] Sample data exists for all four resources
- [ ] `GET /states` and `GET /regions` work
- [ ] Region responses are a list of records with `id`
- [ ] Initial unit tests pass, including regions
- [ ] Development instructions are documented
- [ ] Team pull requests are reviewed and merged

---

## 4. Week 2 — Initial API Endpoints

**Goal:** Finish read-by-id for the existing resources, add the first neighborhood and property reads, and connect the app to MongoDB.

| Member | Commit 1 | Commit 2 |
|--------|----------|----------|
| 1 — States | Implement GET state by ID | Implement POST state with tests |
| 2 — Regions | Implement GET region by ID | Add `region_id` on states and validate it against existing regions |
| 3 — Neighborhoods | Implement GET all neighborhoods | Implement GET neighborhood by ID with tests |
| 4 — Properties | Implement GET all properties | Implement GET property by ID with tests |
| 5 — Infrastructure | Make `connect_db()` and `is_db_up()` real, and point state and region reads at `seDB` | Add database test fixtures |

`GET /states` and `GET /regions` already exist. Do not reimplement them as new routes.

Each new endpoint must include tests and Swagger documentation before its feature is considered complete. Add a flask-restx model for regions. The `State` model already exists.

---

## 5. Week 3 — CRUD Operations

**Goal:** Complete the remaining CRUD operations.

| Member | Commit 1 | Commit 2 |
|--------|----------|----------|
| 1 — States | Implement PATCH state | Implement DELETE state |
| 2 — Regions | Implement POST region | Implement PATCH/DELETE region |
| 3 — Neighborhoods | Implement POST neighborhood | Implement PATCH/DELETE neighborhood |
| 4 — Properties | Implement POST property | Implement PATCH/DELETE property |
| 5 — Infrastructure | Move create, update, and delete for states and regions onto `data/db_connect.py` | Add database integration tests |

All CRUD operations should:
- Validate incoming data
- Return appropriate HTTP status codes
- Handle missing or invalid resources
- Reject a `region_id`, `state_id`, or `neighborhood_id` that does not exist
- Include unit tests
- Include Swagger documentation

---

## 6. Week 4 — Relationships & Search

**Goal:** Support geographic hierarchy navigation and property queries.

| Member | Commit 1 | Commit 2 |
|--------|----------|----------|
| 1 — States | GET neighborhoods within a state | Test nested state queries |
| 2 — Regions | GET states within a region | Test nested region queries |
| 3 — Neighborhoods | GET properties within a neighborhood | Add neighborhood filtering tests |
| 4 — Properties | Implement price filtering | Implement bedroom/bathroom filtering |
| 5 — Infrastructure | Implement RAM caching | Add cache invalidation tests |

Nested routes:
- `GET /regions/{id}/states`
- `GET /states/{id}/neighborhoods`
- `GET /neighborhoods/{id}/properties`

Additional requirements:
- Validate parent-child relationships.
- Prevent orphaned records.
- Define appropriate deletion behavior when a region, state, or neighborhood still has children.
- Invalidate affected cached results after mutations.

---

## 7. Week 5 — CI/CD & Deployment

**Goal:** Prepare the API for cloud deployment.

| Member | Commit 1 | Commit 2 |
|--------|----------|----------|
| 1 — States | Expand state endpoint tests | Fix integration issues |
| 2 — Regions | Expand region endpoint tests | Improve error handling |
| 3 — Neighborhoods | Expand neighborhood tests | Improve query validation |
| 4 — Properties | Add combined search filters | Test property search edge cases |
| 5 — Infrastructure | Replace `deploy.sh` and the course Atlas URI with the team's cloud host | Run that deploy from `.github/workflows/main.yml` |

`deploy.sh` currently targets the PythonAnywhere account `Fall2023`. The workflow's deploy step is commented out and expects `DEMO_PA_PWD`. Replace both. Do not revive `.travis.yml`.

All members should help verify that their endpoints work in the deployed environment.

---

## 8. Week 6+ — Improvements & Finalization

### Required Work
- [ ] Complete missing features
- [ ] Improve unit test coverage
- [ ] Finalize Swagger documentation
- [ ] Verify all database operations against `seDB`
- [ ] Review caching behavior
- [ ] Test deployed API endpoints
- [ ] Fix integration bugs
- [ ] Decide whether `states/raw_data/states.csv` coordinates belong on the state record

### Optional Features
- [ ] Geographic proximity search
- [ ] Search properties by distance
- [ ] Property price statistics
- [ ] Pagination and sorting
- [ ] Neighborhood safety information using reliable external data
- [ ] More advanced property filters

Optional features should only be started after the required functionality is complete.

---

## 9. API Endpoints

### Already implemented

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/hello` | Liveness check. Returns `{"hello": "world"}`. |
| GET | `/endpoints` | Sorted list of registered routes |
| GET | `/states` | States from `STATE_TEST_DATA`, under `"States:"` |
| GET | `/regions` | Regions from `REGION_TEST_DATA`, under `"Regions:"` |

### States

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/states` | Retrieve all states (exists) |
| GET | `/states/{id}` | Retrieve a state |
| POST | `/states` | Create a state |
| PATCH | `/states/{id}` | Update a state |
| DELETE | `/states/{id}` | Delete a state |

### Regions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/regions` | Retrieve all regions (exists; response becomes a list) |
| GET | `/regions/{id}` | Retrieve a region |
| POST | `/regions` | Create a region |
| PATCH | `/regions/{id}` | Update a region |
| DELETE | `/regions/{id}` | Delete a region |

### Neighborhoods

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/neighborhoods` | Retrieve all neighborhoods |
| GET | `/neighborhoods/{id}` | Retrieve a neighborhood |
| POST | `/neighborhoods` | Create a neighborhood |
| PATCH | `/neighborhoods/{id}` | Update a neighborhood |
| DELETE | `/neighborhoods/{id}` | Delete a neighborhood |

### Properties

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/properties` | Retrieve all properties |
| GET | `/properties/{id}` | Retrieve a property |
| POST | `/properties` | Create a property |
| PATCH | `/properties/{id}` | Update a property |
| DELETE | `/properties/{id}` | Delete a property |

### Additional Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/regions/{id}/states` | States in a region |
| GET | `/states/{id}/neighborhoods` | Neighborhoods in a state |
| GET | `/neighborhoods/{id}/properties` | Properties in a neighborhood |
| GET | `/properties/search` | Search and filter properties |
| GET | `/health` | Check API health |
| GET | `/stats` | Retrieve geographic statistics |

**Total planned:** 14 unique resource URL patterns, supporting at least 26 method-specific API operations, plus the existing `/hello` and `/endpoints` routes.

---

## 10. Git Workflow

Each member should work on a dedicated feature branch from `main`.

The root makefile target `github` commits everything and pushes `master`. Do not use it. `.travis.yml` is unused.

### Suggested Branch Names

- `feature/states-api`
- `feature/regions-api`
- `feature/neighborhoods-api`
- `feature/properties-api`
- `feature/infrastructure`

### Weekly Requirements

Each member must:
1. Complete at least 2 meaningful commits per week.
2. Write tests for implemented functionality.
3. Update Swagger documentation when adding or changing endpoints.
4. Push work to their feature branch.
5. Open a pull request for review.
6. Resolve merge conflicts and ensure tests pass.

### Example Git Commands

```bash
git switch -c feature/states-api

# After completing the first task
git add .
git commit -m "docs: define real estate API architecture"

# After completing the second task
git add .
git commit -m "test: cover existing states endpoint contract"

git push -u origin feature/states-api
```

### Pull Request Checklist

- [ ] Code follows project conventions
- [ ] Changes are scoped to the assigned feature
- [ ] New functions and endpoints have tests
- [ ] Relevant Swagger documentation is updated
- [ ] Existing tests pass through `make all_tests`
- [ ] No unrelated files were modified
- [ ] `security/`, `examples/`, `data/manus/`, and `data/bkup/` were left unchanged

---

## 11. Definition of Done

A feature is complete when:

1. Its functionality is implemented.
2. Input validation and error handling are included.
3. Required unit tests pass.
4. Swagger documentation is updated.
5. Changes are reviewed and merged.
6. The feature works with the other API resources.
7. Parent ids refer to records that exist in the parent collection.

---

## Project Milestones

| Milestone | Target |
|-----------|--------|
| Week 1 | Schema aligned with the repo, mock data, region list response, reliable tests |
| Week 2 | Read endpoints and `seDB` for states and regions |
| Week 3 | Complete CRUD functionality |
| Week 4 | Nested queries, filters, caching |
| Week 5 | CI/CD and cloud deployment |
| Week 6+ | Testing, documentation, optional features |

**Project Priority:** Complete the required API functionality, tests, database persistence, and deployment before adding advanced real estate features.
