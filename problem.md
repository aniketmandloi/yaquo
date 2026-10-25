# Problem Setting

You are a product developer tasked with developing and delivering a customized software product for a client. The product manager has provided the following context, directions, and requirements. Your process should include:

- Gaining knowledge of the domain through research and information gathering.
- Developing the first version of the product based on the provided information.
- Presenting and pitching the product to the client.
- Explaining the software design and implementation to an internal technical lead for review.

## Requirement (from Product Manager)

The client is an energy utility company in the UK. They need to purchase electricity from the wholesale market to serve their consumers. The specific team you are targeting is responsible for procuring the required power from the UK day-ahead market.

To meet consumer electricity demand, the team needs to calculate how much power must be purchased (e.g., from thermal plants) in addition to what is generated from renewable sources like wind. Since renewable generation is weather-dependent and must be forecasted, power purchase decisions must be made one day before delivery. This requires reliable renewable generation forecasts.

**The web application must enable the team to:**

1. Clearly understand the latest renewable generation forecasts available when making day-ahead market purchase decisions.
2. Quantitatively evaluate the accuracy of these renewable generation forecasts to factor quantified error into decision-making.

**Scope limitation:**  
Only national-level actuals and forecasts of wind power generation from Elexon are in scope—no other data sources should be used.

### 2.1 Actual Generation

- Source: [FUELHH API documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/FUELHH/stream)
- Use values with `"fuelType": "WIND"`
- Relevant fields:
  - `startTime`: target time (30-minute resolution)
  - `generation`: generated wind power

### 2.2 Forecasted Generation

- Source: [WINDFOR API documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/datasets/WINDFOR/stream)
- Relevant fields:
  - `startTime`: matches the "startTime" in the actuals dataset
  - `publishTime`: when the forecast was created
  - `generation`: forecasted wind power

**Timeframe:**

- Only consider data relevant for purchase decisions in **January 2026**.

**Technical requirements:**

- **Frontend:** React
- **Backend:** Python
- **Containerization:** Docker
- **Deployment:** Vercel or Heroku
- You may use AI tools to assist (note this explicitly in the README).
- Do not spend more than 16 hours on the assignment.

---

## Deliverables

### 3.1 Video Demo

- Create an **unlisted YouTube video** as a guide, consisting of two parts:
  - **Part 1:** Present the portal and analysis to the customer as the outcome of a pilot project (max 5 minutes).
  - **Part 2:** Present the work to the technical lead for review, explaining architecture, design, codebase, and key development practices (max 5 minutes).
- **Total video duration:** Maximum 10 minutes.
- The evaluation will start with the video. Do not submit without it.

### 3.2 Repo

- Create a **public GitHub repo** (use an anonymous/random name, e.g., "kjhwr").
- README should include:
  - Details of files and directories
  - How to start the application
  - Link to the Vercel/Heroku app

### 3.3 Submission Form

- Submit all details via the "Full Stack SWE challenge submission v4" form.
- Verify all submitted URLs work in incognito mode to ensure access.
