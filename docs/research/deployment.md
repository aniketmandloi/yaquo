# Deployment research

Checked against official documentation on 25 October 2026. No app was created, deployment attempted, or paid resource provisioned.

## Recommendation

Use one Heroku Basic web dyno, with a Docker image containing the built React frontend and a Python HTTP backend that serves both the frontend and API. This is a design recommendation: a single origin and artifact reduce deployment work within the assignment's 16-hour limit. Heroku accepts Docker images directly; Basic does not sleep and is currently listed at $7 per month. [Container deployment](https://devcenter.heroku.com/articles/container-registry-and-runtime), [Basic behavior](https://www.heroku.com/dynos/configure/), [pricing](https://www.heroku.com/pricing/)

Ask the user to choose the hosting budget before provisioning. Heroku requires account verification using a payment method to create apps, deploy code, and use dynos. Existing credentials and billing approval have not been checked. [Account verification](https://devcenter.heroku.com/articles/account-verification)

## Essential hosting constraints

| Option | Verified behavior | Implication for this pilot |
| --- | --- | --- |
| Heroku container runtime | Docker registry deployment is documented for Cedar apps. The HTTP server must listen on the assigned `$PORT`. Images must target `linux/amd64`; Heroku's registry requires Docker manifest V2 schema 2 rather than OCI manifests. | Use a multi-stage frontend/Python image and verify the produced architecture and manifest before pushing, particularly on Apple Silicon. |
| Vercel | Container Runtime is in beta on all plans. It accepts a root Dockerfile with the Container preset; `Dockerfile.vercel` gives the container preset priority over framework detection. Images run as HTTP functions, separate from Sandbox execution. | A valid alternative; do not claim Vercel cannot deploy Docker. Account access and an actual deployment still need verification. |

Sources: [Heroku container constraints](https://devcenter.heroku.com/articles/container-registry-and-runtime), [Vercel Container Runtime](https://vercel.com/docs/functions/runtimes/container), [Functions versus Sandbox](https://vercel.com/kb/guide/docker).

Heroku Eco is listed at $5 per month and sleeps after 30 minutes of inactivity; Basic is preferable for an evaluator opening the demo at an unknown time. Basic's published memory is 0.5 GB, so measure application memory and avoid loading unnecessary raw data into multiple worker processes. [Heroku pricing](https://www.heroku.com/pricing/), [dyno behavior](https://www.heroku.com/dynos/configure/)

Vercel Hobby is free but restricted to personal, non-commercial use. Do not assume a client pilot qualifies without checking the intended use. Its Container Runtime uses the standard Function limits and Active CPU billing; idle production instances scale down after five minutes. Registry storage is separately listed at $0.10 per GB, and registry quotas are documented for Hobby, Pro, and Enterprise. The registry is also labeled beta. This research does not establish the user's account entitlements or total deployment cost. [Hobby plan](https://vercel.com/docs/plans/hobby), [Container Runtime](https://vercel.com/docs/functions/runtimes/container), [registry limits and pricing](https://vercel.com/docs/container-registry/limits-and-pricing)

## Containerization versus hosting

The assignment separately requires Docker and deployment to Vercel or Heroku; it does not explicitly say the public host must run the submitted Docker image. Vercel also supports Python applications through its Python runtime, including FastAPI and Flask. A source deployment plus a working Docker deliverable is therefore an interpretation of the brief, not proof of evaluator expectations. Hosting the actual image on Heroku avoids this ambiguity. [Assignment](../../problem.md), [Vercel Python runtime](https://vercel.com/docs/functions/runtimes/python)

## Implementation and delivery checks

These are proposed checks, not completed verification:

- Build and run the Docker image with a supplied port; check the frontend, API, and refresh on frontend routes.
- If using a bundled January dataset, include provenance and an explicit refresh procedure; do not depend on mutable runtime files for the only copy.
- Verify automated checks before deployment, then have the user inspect the public application in incognito mode as required by the assignment.
- Keep the public URL working through evaluation; the owner must decide the retention period and hosting budget.
- Include Docker startup instructions, the hosted URL, AI assistance disclosure, and the video link in the README/submission materials.

The final four points derive from the assignment or are delivery recommendations, rather than platform guarantees. No running application's compatibility, performance, public access, or deployment success has been verified.
