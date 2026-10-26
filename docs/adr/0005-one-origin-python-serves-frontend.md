# 0005: Serve the React build and the API from one Python process

Status: Accepted

## Context

The evaluator should open one public URL. Separate frontend and backend hosts would need CORS configuration and two deployments, and each adds a point of failure within the 16-hour limit.

## Decision

FastAPI serves the API under `/api` and serves the built React app from `frontend/dist`. Unknown paths return `index.html`, so refreshing a page keeps working. Unknown `/api` paths return 404. Requests that resolve outside the frontend folder are not served; the app returns `index.html` for them. A multi-stage Dockerfile builds both parts into one image.

## Consequences

- One origin and one artifact to build, test and deploy.
- The frontend cannot scale separately from the API. For a pilot with one evaluator, that is acceptable.

Sources: [`docs/research/deployment.md`](../research/deployment.md), Recommendation; `backend/tests/test_frontend_serving.py`.
