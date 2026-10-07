
# Geographic Real Estate API — Project Plan

## Project Overview

Our goal is to build a RESTful API server for geographic real estate data using the existing geodata2026 project.

The API will support CRUD (Create, Read, Update, Delete) operations on geographic and housing data.

### Data Hierarchy

State → Region → Neighborhood → Property

Example:
- State: New York
- Region: New York City
- Neighborhood: Chelsea
- Property: 123 W 20th St, Apartment 4B

We will initially use mock data and gradually integrate database persistence, search functionality, caching, testing, and cloud deployment.

## Project Requirements

- [ ] Implement CRUD operations for all major resources
- [ ] Create at least 12 API endpoints
- [ ] Store data in a database
- [ ] Write unit tests for every endpoint and other functions
- [ ] Document endpoints using Swagger
- [ ] Implement in-memory caching where practical
- [ ] Set up CI/CD for automated testing and deployment
- [ ] Deploy the API server to the cloud

---

## 1. Team Responsibilities

Each member will own a primary feature or area of the project.

### Member 1 — States API & Integration
- Implement CRUD operations for states
- Define shared API conventions and response formats
- Coordinate integration between resources
- Write tests and Swagger documentation for state endpoints
- Review and integrate team pull requests

### Member 2 — Regions API
- Implement CRUD operations for regions
- Establish relationships between regions and states
- Validate region data and parent IDs
- Write tests and Swagger documentation for region endpoints

### Member 3 — Neighborhoods API
- Implement CRUD operations for neighborhoods
- Establish relationships between neighborhoods and regions
- Implement neighborhood lookup functionality
- Write tests and Swagger documentation for neighborhood endpoints

### Member 4 — Properties API
- Implement CRUD operations for properties
- Define property attributes (price, bedrooms, bathrooms, etc.)
- Implement property search and filtering
- Write tests and Swagger documentation for property endpoints

### Member 5 — Database & Infrastructure
- Configure database connectivity and persistence
- Create shared database utilities and seed-data support
- Set up CI/CD workflows
- Configure shared testing infrastructure
- Implement caching utilities
- Coordinate cloud deployment

**Note:** Every member is responsible for testing and documenting their own features. Member 5 handles shared infrastructure, not everyone's tests.

---

## 2. Data Models

All collections will use consistent IDs and reference their parent resources.

### State
- id
- name
- abbreviation

### Region
- id
- name
- state_id

### Neighborhood
- id
- name
- region_id

### Property
- id
- address
- neighborhood_id
- price
- bedrooms
- bathrooms
- latitude
- longitude

### Data Conventions
- IDs and parent IDs should use a consistent format.
- Every region must reference an existing state.
- Every neighborhood must reference an existing region.
- Every property must reference an existing neighborhood.
- All required fields should be validated.
- Mock data should use consistent IDs across collections.

---

## 3. Week 1 — Project Foundation

**Deadline: October 8, 2026**

### Goal

Establish the initial data models, sample data, API architecture, and development infrastructure.

Each member must complete **2 meaningful commits**.

### Member 1 — States & API Architecture

**Commit 1: Define API Structure**
- [ ] Create `docs/api-design.md`
- [ ] Document the four resources and relationships
- [ ] Define naming conventions and endpoint patterns
- [ ] Establish expected request/response formats

Commit message:
`docs: define real estate API architecture`

**Commit 2: Initial States Endpoint**
- [ ] Implement `GET /states` using mock data
- [ ] Return a JSON list of states
- [ ] Add unit tests for the endpoint

Commit message:
`feat: implement initial states endpoint with tests`

### Member 2 — State and Region Data

**Commit 1: Add Mock Data**
- [ ] Create sample state records
- [ ] Create sample region records
- [ ] Associate each region with a state using `state_id`

Commit message:
`feat: add mock state and region data`

**Commit 2: Region Data Validation**
- [ ] Add validation for required region fields
- [ ] Verify that region state references are valid
- [ ] Write unit tests for validation functions

Commit message:
`test: add region data validation and tests`

### Member 3 — Neighborhood Data

**Commit 1: Add Neighborhood Mock Data**
- [ ] Create at least 5 sample neighborhoods
- [ ] Include `region_id` for each neighborhood
- [ ] Ensure data follows the agreed schema

Commit message:
`feat: add neighborhood mock data`

**Commit 2: Neighborhood Validation**
- [ ] Validate required neighborhood fields
- [ ] Verify neighborhood-to-region relationships
- [ ] Write unit tests for validation functions

Commit message:
`test: add neighborhood data validation tests`

### Member 4 — Property Data

**Commit 1: Add Property Mock Data**
- [ ] Create at least 5 sample properties
- [ ] Include address, price, bedrooms, and bathrooms
- [ ] Add geographic coordinates
- [ ] Associate properties with neighborhoods

Commit message:
`feat: add mock real estate property data`

**Commit 2: Property Validation**
- [ ] Validate required property fields
- [ ] Validate price and numeric attributes
- [ ] Write unit tests for property validation

Commit message:
`test: add property data validation tests`

### Member 5 — Database & Infrastructure

**Commit 1: Database Planning**
- [ ] Document the database schema
- [ ] Define collection relationships
- [ ] Document local development setup
- [ ] Outline how mock data will be seeded

Commit message:
`docs: define database schema and setup`

**Commit 2: Testing Infrastructure**
- [ ] Review the existing testing configuration
- [ ] Set up or update the automated test workflow
- [ ] Verify that tests run successfully
- [ ] Document how to run tests locally

Commit message:
`ci: configure automated testing workflow`

### Week 1 Completion Checklist

- [ ] All 5 members have made 2 commits each
- [ ] Data models have been agreed upon
- [ ] Sample data exists for all four resources
- [ ] At least one API endpoint works
- [ ] Initial unit tests pass
- [ ] Development instructions are documented
- [ ] Team pull requests are reviewed and merged

---

## 4. Week 2 — Initial API Endpoints

**Goal:** Implement initial read operations and database integration.

| Member | Commit 1 | Commit 2 |
|--------|----------|----------|
| 1 — States | Implement GET state by ID | Implement POST state with tests |
| 2 — Regions | Implement GET all regions | Implement GET region by ID with tests |
| 3 — Neighborhoods | Implement GET all neighborhoods | Implement GET neighborhood by ID with tests |
| 4 — Properties | Implement GET all properties | Implement GET property by ID with tests |
| 5 — Infrastructure | Configure database connection | Add database test fixtures |

Each endpoint must include tests and Swagger documentation before its feature is considered complete.

---

## 5. Week 3 — CRUD Operations

**Goal:** Complete the remaining CRUD operations.

| Member | Commit 1 | Commit 2 |
|--------|----------|----------|
| 1 — States | Implement PATCH state | Implement DELETE state |
| 2 — Regions | Implement POST region | Implement PATCH/DELETE region |
| 3 — Neighborhoods | Implement POST neighborhood | Implement PATCH/DELETE neighborhood |
| 4 — Properties | Implement POST property | Implement PATCH/DELETE property |
| 5 — Infrastructure | Implement persistence utilities | Add database integration tests |

All CRUD operations should:
- Validate incoming data
- Return appropriate HTTP status codes
- Handle missing or invalid resources
- Include unit tests
- Include Swagger documentation

---

## 6. Week 4 — Relationships & Search

**Goal:** Support geographic hierarchy navigation and property queries.

| Member | Commit 1 | Commit 2 |
|--------|----------|----------|
| 1 — States | GET regions within a state | Test nested state queries |
| 2 — Regions | GET neighborhoods within a region | Test nested region queries |
| 3 — Neighborhoods | GET properties within a neighborhood | Add neighborhood filtering tests |
| 4 — Properties | Implement price filtering | Implement bedroom/bathroom filtering |
| 5 — Infrastructure | Implement RAM caching | Add cache invalidation tests |

Additional requirements:
- Validate parent-child relationships.
- Prevent orphaned records.
- Define appropriate deletion behavior.
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
| 5 — Infrastructure | Configure cloud deployment | Automate deployment through CI/CD |

All members should help verify that their endpoints work in the deployed environment.

---

## 8. Week 6+ — Improvements & Finalization

### Required Work
- [ ] Complete missing features
- [ ] Improve unit test coverage
- [ ] Finalize Swagger documentation
- [ ] Verify all database operations
- [ ] Review caching behavior
- [ ] Test deployed API endpoints
- [ ] Fix integration bugs

### Optional Features
- [ ] Geographic proximity search
- [ ] Search properties by distance
- [ ] Property price statistics
- [ ] Pagination and sorting
- [ ] Neighborhood safety information using reliable external data
- [ ] More advanced property filters

Optional features should only be started after the required functionality is complete.

---

## 9. Planned API Endpoints

### States

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/states` | Retrieve all states |
| GET | `/states/{id}` | Retrieve a state |
| POST | `/states` | Create a state |
| PATCH | `/states/{id}` | Update a state |
| DELETE | `/states/{id}` | Delete a state |

### Regions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/regions` | Retrieve all regions |
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
| GET | `/states/{id}/regions` | Regions in a state |
| GET | `/regions/{id}/neighborhoods` | Neighborhoods in a region |
| GET | `/neighborhoods/{id}/properties` | Properties in a neighborhood |
| GET | `/properties/search` | Search and filter properties |
| GET | `/health` | Check API health |
| GET | `/stats` | Retrieve geographic statistics |

**Total planned:** 14 unique URL patterns, supporting at least 26 method-specific API operations.

---

## 10. Git Workflow

Each member should work on a dedicated feature branch.

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
git commit -m "feat: implement states endpoint with tests"

git push -u origin feature/states-api
```

### Pull Request Checklist

- [ ] Code follows project conventions
- [ ] Changes are scoped to the assigned feature
- [ ] New functions and endpoints have tests
- [ ] Relevant Swagger documentation is updated
- [ ] Existing tests pass
- [ ] No unrelated files were modified

---

## 11. Definition of Done

A feature is complete when:

1. Its functionality is implemented.
2. Input validation and error handling are included.
3. Required unit tests pass.
4. Swagger documentation is updated.
5. Changes are reviewed and merged.
6. The feature works with the other API resources.

---

## Project Milestones

| Milestone | Target |
|-----------|--------|
| Week 1 | Architecture, schemas, mock data, initial endpoint |
| Week 2 | Read endpoints and database integration |
| Week 3 | Complete CRUD functionality |
| Week 4 | Nested queries, filters, caching |
| Week 5 | CI/CD and cloud deployment |
| Week 6+ | Testing, documentation, optional features |

**Project Priority:** Complete the required API functionality, tests, database persistence, and deployment before adding advanced real estate features.
