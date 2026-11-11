# API Design

Short reference for how our real estate API is structured. See
`planning/TEAM_PLAN.md` for who owns what and the week-by-week plan.

## Resources

The hierarchy is Region -> State -> Neighborhood -> Property.

| Resource     | Parent       | Parent field      | Endpoints                                 |
|--------------|--------------|-------------------|-------------------------------------------|
| Region       | none         | none              | list, create, get, update, delete         |
| State        | Region       | `region_id`       | list, create, get, update, delete         |
| Neighborhood | State        | `state_id`        | list, create, get, update, delete         |
| Property     | Neighborhood | `neighborhood_id` | list, create, get, update, delete, search |

Example: Northeast (`NE`) -> New York (`NY`) -> Chelsea -> 123 W 20th St.

## IDs

- States and regions use their two-letter code as `id` (`NY`, `NE`).
- Neighborhoods and properties use non-empty string ids.
- A parent field stores the parent's `id`.
- Creating a state requires a two-letter `region_id` referencing an existing
  region. State updates may omit `region_id` to keep the current parent;
  supplying null, an invalid code, or an unknown region returns HTTP 400.

## Endpoint patterns

- Plural, lowercase collection names: `/states`, `/regions`,
  `/neighborhoods`, `/properties`.
- One item: `/<collection>/<id>`.
- Nested lists: `/states/<id>/neighborhoods`.
- `GET` reads, `POST` creates, `PATCH` updates, `DELETE` removes.

## Current endpoints

| Method | Path                                          | Description                           |
|--------|-----------------------------------------------|---------------------------------------|
| GET    | `/hello`                                      | Check that the server is running      |
| GET    | `/health`                                     | API and MongoDB health check          |
| GET    | `/endpoints`                                  | List all available endpoints          |
| GET    | `/regions`                                    | List all regions                      |
| POST   | `/regions`                                    | Create a region                       |
| GET    | `/regions/{region_id}`                        | Get a region                          |
| PATCH  | `/regions/{region_id}`                        | Update a region                       |
| DELETE | `/regions/{region_id}`                        | Delete a region                       |
| GET    | `/regions/{region_id}/states`                 | List the states in a region           |
| GET    | `/states`                                     | List all states                       |
| POST   | `/states`                                     | Create a state                        |
| GET    | `/states/{state_id}`                          | Get a state                           |
| PATCH  | `/states/{state_id}`                          | Update a state                        |
| DELETE | `/states/{state_id}`                          | Delete a state                        |
| GET    | `/states/{state_id}/neighborhoods`            | List the neighborhoods in a state     |
| GET    | `/neighborhoods`                              | List all neighborhoods                |
| POST   | `/neighborhoods`                              | Create a neighborhood                 |
| GET    | `/neighborhoods/{neighborhood_id}`            | Get a neighborhood                    |
| PATCH  | `/neighborhoods/{neighborhood_id}`            | Update a neighborhood                 |
| DELETE | `/neighborhoods/{neighborhood_id}`            | Delete a neighborhood                 |
| GET    | `/neighborhoods/{neighborhood_id}/properties` | List the properties in a neighborhood |
| GET    | `/properties`                                 | List all properties                   |
| POST   | `/properties`                                 | Create a property                     |
| GET    | `/properties/search`                          | Search and filter properties          |
| GET    | `/properties/{property_id}`                   | Get a property                        |
| PATCH  | `/properties/{property_id}`                   | Update a property                     |
| DELETE | `/properties/{property_id}`                   | Delete a property                     |

Swagger docs are served by flask-restx at `/swagger.json`.

### States within a region

`GET /regions/{region_id}/states` returns only states whose `region_id`
matches the requested region, wrapped as `{"States:": [...]}`. Each state
includes its `region_id`. An existing region with no states returns HTTP 200
with `{"States:": []}`. A missing region returns 404; an unavailable region
or state lookup returns 503.

`DELETE /regions/{region_id}` returns 409 while any state references the
region. Reassign or delete those states before deleting their region.

### Neighborhoods within a state

`GET /states/{state_id}/neighborhoods` returns the neighborhoods whose
`state_id` matches, wrapped as `{"Neighborhoods:": [...]}`. An existing state
with no neighborhoods returns HTTP 200 with an empty list. A missing state
returns 404, and an unavailable database returns 503.

`DELETE /states/{state_id}` returns 409 while any neighborhood references
the state. Reassign or delete those neighborhoods before deleting the state.

## Response formats

List endpoints wrap the collection in a labeled object:

```json
{
  "States:": [
    {
      "id": "AL",
      "name": "Alabama",
      "capital": "Montgomery",
      "population": 4903185,
      "area_sq_miles": 52420,
      "region_id": "SE"
    }
  ]
}
```

A single state is wrapped under `"State:"`, and regions use the same pattern
under `"Regions:"` and `"Region:"`. A successful `DELETE` returns 204 with no
body. Errors return a JSON object with a `message` field.

## Status codes

| Code | Meaning                                                  |
|------|----------------------------------------------------------|
| 200  | Success                                                  |
| 201  | Created (`POST`)                                         |
| 204  | Deleted (`DELETE`)                                       |
| 400  | Invalid or missing fields                                |
| 404  | Item not found                                           |
| 409  | Item already exists, or it still has children (`DELETE`) |
| 503  | Database unavailable                                     |
