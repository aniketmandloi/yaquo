# 0008: Deploy the container image to a Render free web service

Status: Accepted, deployment pending. Supersedes [0006](0006-heroku-basic-container.md).

## Context

The Heroku account could not be verified because the payment card was declined. The evaluator still needs one public URL. The brief names Vercel or Heroku as the deployment targets, so Render is outside the brief's list. Vercel Hobby is limited to personal, non-commercial use, and Vercel Pro costs $20 per developer seat per month.

## Decision

Deploy the same Docker image as a Render web service on the free instance type, connected to the GitHub repository. Render builds the root `Dockerfile` and serves on the port in `$PORT`, bound to `0.0.0.0`, which the image already does. `heroku.yml` is removed because nothing reads it.

## Consequences

- The app costs nothing to run.
- The free instance spins down after 15 minutes without traffic. The first request after that takes about a minute while it restarts. Open the URL shortly before the evaluation, and say so in the README.
- Render's documentation says free services are not for production. This is a demonstration, so the risk is limited to the evaluator's first load.
- Free services are suspended for the rest of the month if their 750 instance hours run out. A single service running all month uses about 744 hours.
- The brief names Vercel or Heroku. Using Render is a departure from the brief, so the submission should state it openly.
- The data is inside the image, so the instance has no disk to lose.

Sources: [Render free instances](https://render.com/docs/free), [Render web services](https://render.com/docs/web-services), [Render Docker](https://render.com/docs/docker).
