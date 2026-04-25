# API contract baseline

This file fixes the current external contract of critical endpoints during backend refactoring.
The goal is to keep response shapes and status codes stable while internals move to services/repositories.

## Tasks

- `POST /api/v1/tasks/distribute`
  - `200` with `{ "message": string }`
  - On missing `ASSIGNED` status: returns `200` with cancellation message (legacy behavior)
- `GET /api/v1/tasks/me`
  - `200` with:
    - `tasks: TaskMePublic[]`
    - `route: [ [lon, lat], ... ] | null`
    - `start_location: LocationPublic`
- `PATCH /api/v1/tasks/{task_id}/complete`
  - `404` if task not found
  - `403` if task belongs to another employee
  - `500` if `COMPLETED` status missing
  - `200` returns `TaskPublic`
- `PATCH /api/v1/tasks/{task_id}/skip`
  - `404` if task not found
  - `403` if task belongs to another employee
  - `500` if `SKIPPED` status missing
  - `200` returns `TaskPublic`

## Locations

- `POST /api/v1/locations/`
  - `503` when geocoding is unavailable
  - `400` when address is not found
  - `200` returns `LocationPublic`
- `PUT /api/v1/locations/{id}`
  - `404` if location not found
  - same geocoding errors as create
  - `200` returns `LocationPublic`

## Agent point events

- `POST /api/v1/agent-point-events/`
  - `422` on schema validation mismatch
  - `200` returns `AgentPointEventPublic`
- `PUT /api/v1/agent-point-events/{id}`
  - `404` if event not found
  - `422` on schema validation mismatch
  - `200` returns `AgentPointEventPublic`
