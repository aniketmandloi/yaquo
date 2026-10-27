# 0006: Deploy the container image to one Heroku Basic dyno

Status: Superseded by [0008](0008-render-free-web-service.md). The Heroku card payment was declined.

## Context

The brief allows Vercel or Heroku. The evaluator needs the app to be available whenever they open it. Eco ($5 a month) sleeps after 30 minutes idle. Vercel Hobby is limited to personal, non-commercial use, and Vercel Pro costs more per developer seat. Render's free tier is not for production and is not in the brief's list of hosts.

## Decision

Deploy the Docker image to one Heroku Basic dyno ($7 a month) using the container stack. `heroku.yml` makes Heroku build the image, which avoids architecture problems when building on Apple Silicon. The user accepted the $7 cost in the spec.

## Consequences

- The app stays up for the evaluator. Deleting the app after the evaluation stops the charge.
- Heroku needs a verified account and a payment method before it can create a paid app.
- The deployed URL and working status are not confirmed until the deployment is checked in an incognito window.

Sources: [`docs/research/deployment.md`](../research/deployment.md); `heroku.yml`; [issue #4](https://github.com/aniketmandloi/yaquo/issues/4).
