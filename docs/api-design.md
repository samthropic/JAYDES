# API Design

Short reference for how our real estate API is structured. See
`planning/TEAM_PLAN.md` for who owns what and the week-by-week plan.

## Resources

The hierarchy is Region -> State -> Neighborhood -> Property.

| Resource     | Parent       | Parent field      | Status             |
|--------------|--------------|-------------------|--------------------|
| Region       | none         | none              | `GET` exists       |
| State        | Region       | `region_id` (planned) | `GET` exists   |
| Neighborhood | State        | `state_id`        | planned            |
| Property     | Neighborhood | `neighborhood_id` | planned            |

Example: Northeast (`NE`) -> New York (`NY`) -> Chelsea -> 123 W 20th St.

## IDs

- States and regions use their two-letter code as `id` (`NY`, `NE`).
- Neighborhoods and properties use non-empty string ids.
- A parent field stores the parent's `id`.

## Endpoint patterns

- Plural, lowercase collection names: `/states`, `/regions`,
  `/neighborhoods`, `/properties`.
- One item: `/<collection>/<id>`.
- Nested lists: `/states/<id>/neighborhoods`.
- `GET` reads, `POST` creates, `PATCH` updates, `DELETE` removes.

## Current endpoints

| Method | Path         | Description                            |
|--------|--------------|----------------------------------------|
| GET    | `/hello`     | Check that the server is running       |
| GET    | `/endpoints` | List all available endpoints           |
| GET    | `/states`    | List all states                        |
| GET    | `/regions`   | List all regions                       |

Swagger docs are served by flask-restx at `/swagger.json`.

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
      "area_sq_miles": 52420
    }
  ]
}
```

Regions use the same pattern under the `"Regions:"` key.

## Status codes

| Code | Meaning                                  |
|------|------------------------------------------|
| 200  | Success                                  |
| 201  | Created (`POST`)                         |
| 400  | Invalid or missing fields                |
| 404  | Item not found                           |
| 409  | Item already exists                      |
| 503  | Database unavailable                     |

Only 200 and 503 are in use today. The others will be used as the
create, update and delete endpoints are added.
