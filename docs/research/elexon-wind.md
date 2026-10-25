# Elexon wind pilot: evidence and open decisions

Researched 2026-10-25 against first-party documentation and live public API samples. This note informs scope decisions; it does not establish complete January coverage.

## Findings that affect the design

### Historical publications are available, but completeness needs validation

Elexon's developer portal says dataset endpoints support publication-time queries and retrieval of superseded forecasts. The APIs are public and require no API key. Streaming responses are JSON. These statements support using dataset streams for an as-of historical view, but do not guarantee that every historical publication or correction is retained. [Elexon developer portal](https://developer.data.elexon.co.uk/)

The following live queries succeeded during this research:

```text
GET https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream?publishDateTimeFrom=2025-12-31T00%3A00%3A00Z&publishDateTimeTo=2026-01-02T00%3A00%3A00Z

GET https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream?publishDateTimeFrom=2026-01-01T00%3A00%3A00Z&publishDateTimeTo=2026-01-02T02%3A00%3A00Z
```

- WINDFOR returned a JSON array of 1,168 records: 16 distinct publication timestamps, each with 73 target timestamps.
- FUELHH returned 1,060 records across fuel types; 53 records had `fuelType == "WIND"`.
- Both include `dataset`, `publishTime`, `startTime`, and `generation`. FUELHH additionally includes settlement date, settlement period, and fuel type.
- The actuals sample includes a record published exactly at the requested upper bound. Do not assume exclusive API boundaries; filter locally and deduplicate chunk overlaps.
- These are publication filters, not delivery filters: a FUELHH record published at `2026-01-01T00:00:00Z` targeted `2025-12-31T23:30:00Z`. Filter `startTime` separately.

The downloaded samples were examined from temporary files `/tmp/yaquo-elexon-windfor.json` and `/tmp/yaquo-elexon-fuelhh.json`; they are not committed artifacts. Repeat the queries to reproduce the observations. [WINDFOR stream](https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream?publishDateTimeFrom=2025-12-31T00%3A00%3A00Z&publishDateTimeTo=2026-01-02T00%3A00%3A00Z), [FUELHH stream](https://data.elexon.co.uk/bmrs/api/v1/datasets/FUELHH/stream?publishDateTimeFrom=2026-01-01T00%3A00%3A00Z&publishDateTimeTo=2026-01-02T02%3A00%3A00Z)

### Forecast cadence does not match actuals in the sample

WINDFOR publication `2025-12-31T07:30:00Z` has 73 targets from `2025-12-30T21:00:00Z` through `2026-01-02T21:00:00Z`, with all 72 consecutive intervals exactly 60 minutes. FUELHH wind targets in the sample are 30 minutes apart. This is an observed property of the sampled data, not a documented full-month guarantee. [Reproducible WINDFOR query](https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream?publishDateTimeFrom=2025-12-31T00%3A00%3A00Z&publishDateTimeTo=2026-01-02T00%3A00%3A00Z)

**Recommendation:** follow the assignment's explicit same-`startTime` matching rule for the initial pilot. Show the matched sample count and excluded half-hours. Do not silently interpolate forecasts, forward-fill half-hours, or average two actuals into an hourly comparator: those require a separate decision about forecast interval meaning. Profile January before fixing the UI's expected matched count.

### Latest at a decision time differs from latest retrospectively

The same target `2026-01-01T00:00:00Z` appears under multiple publication times with different values. For example, the December 31 07:30 publication gives 19,412 MW; the December 31 09:30 publication gives 19,466 MW. Publications on January 1 also retain this target, after its delivery time. [Reproducible WINDFOR query](https://data.elexon.co.uk/bmrs/api/v1/datasets/WINDFOR/stream?publishDateTimeFrom=2025-12-31T00%3A00%3A00Z&publishDateTimeTo=2026-01-02T00%3A00%3A00Z)

**Recommended as-of rule:** for each delivery `startTime`, choose the record with greatest `publishTime` no later than the chosen decision cutoff on the preceding calendar day. Display the selected publication time and resulting age. Exclude forecasts published after the cutoff from both the decision chart and its accuracy score. This rule is an implementation proposal, not an Elexon market rule.

Elexon's latest-wind documentation advertises up to eight daily publications at nominal times, but the sample has 02:30, 04:30, 07:30, 09:30, 11:30, 15:30, 18:30, and 22:30 UTC. Use actual `publishTime`, not a hard-coded nominal publication timetable. The reason for the offset from documented nominal times has not been established. [Elexon latest-wind documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/forecast/generation/wind/latest)

### Coverage and units

Elexon's wind forecast documentation describes wind farms visible to the system operator with operational metering. Avoid presenting this as every UK wind generator or a utility's own renewable portfolio. The legacy Elexon interface definition defines WIND as power park modules metered by the transmission operator and fuel-type generation in MW. [Elexon wind forecast documentation](https://bmrs.elexon.co.uk/api-documentation/endpoint/forecast/generation/wind/latest), [Elexon interface definition: fuel type and fuel-type generation](https://www.elexon.co.uk/bsc/documents/groups/isg/2022-meetings-isg/253-may/isg253-04b-cp1562-neta-idd-part-1-redline-text-v49/)

**Recommendation:** label the product's data as Elexon reported GB wind generation with an operational-metering coverage note. Keep power charts and forecast errors in MW. Do not infer customer procurement volumes, demand, prices, or trading savings: the permitted datasets do not provide these inputs.

## Decisions the brief leaves open

### Which day-ahead decision cutoff?

There is no single cutoff established by the assignment. Nord Pool's official N2EX support page specifies 09:50 GMT gate closure for next-day delivery. EPEX's official 2023 brochure describes GB hourly day-ahead at 09:20 GMT and half-hourly day-ahead at 15:30 GMT. The brochure is historical evidence, not verification of a January 2026 trading calendar. A blanket 11:00 assumption would therefore be unjustified. [Nord Pool N2EX](https://support.nordpoolgroup.com/support/solutions/articles/8000088463-about-the-n2ex-day-ahead-auction), [EPEX official trading brochure](https://www.epexspot.com/sites/default/files/2023-01/22-10-25_TradingBrochure.pdf)

**Recommendation:** agree on an explicitly labeled pilot cutoff such as 09:00 Europe/London, before the cited morning auctions. If the user wants an exchange-specific cutoff, confirm the exchange and applicable January 2026 rules before describing it as authoritative. These sources inform domain timing only; they are not additional generation data sources.

### January decision dates or January delivery dates?

The phrase “purchase decisions in January 2026” and the presence of delivery-target timestamps allow two plausible boundaries:

| Interpretation | Decision dates | Delivery dates |
| --- | --- | --- |
| January purchase decisions, literally | January 1–31 | January 2–February 1 |
| January delivery analysis | December 31–January 30 | January 1–31 |

These boundaries follow from the brief's one-day-ahead relationship; they are not an API fact. **Recommendation:** prefer the literal decision-date interpretation unless the user chooses otherwise. The UI should always show both decision date and delivery date. Fetch actual publications far enough beyond the delivery range to capture the final actual, then filter delivery targets locally.

## Data-quality and scoring proposals

These are proposed pilot rules, not documented provider guarantees:

- Join only exact UTC target instants with valid finite generation values; never convert missing records to zero.
- Retain forecast publication timestamps. Identical duplicate records may be deduplicated; conflicting values with identical target and publication keys should be surfaced as a data-quality issue rather than arbitrarily selected.
- Choose and document an actual-revision policy. A retrospective pilot can compare against latest retrieved actuals, but must not claim those actuals were available at the earlier decision cutoff.
- Show eligible targets, matched pairs, and missing forecast/actual counts alongside metrics. Distinguish insufficient data from a valid zero error.
- Use signed error `forecast - actual` in MW: positive means wind overforecast, which can leave a purchaser short if treated as available supply. MAE measures typical absolute error; RMSE gives greater weight to large misses; mean signed error shows directional bias. These are mathematical definitions, not claims about predictive performance.
- Monthly realized errors are retrospective analysis. Do not present an uncertainty range calculated using later January outcomes as knowledge available to an early-January purchaser. A decision-time risk estimate needs an explicitly prior evaluation window and sufficient available actuals.

## What remains unverified

- Complete January (and February 1 if needed) coverage, full-month cadence, and missing publications.
- Whether every superseded publication and source correction survives in the API archive.
- Definitive API schema descriptions for all optional filters and error responses. The two tested publication filters work; guessed Swagger URLs returned 404 and the assignment's documentation pages require JavaScript when opened directly.
- Forecast interval semantics beyond target timestamps; this is why the conservative recommendation is exact-start matching.
- The cause of nominal publication-time offsets.
- Historical exchange-specific rules applying to January 2026.
- Operational actuals reconciliation/finality guarantees and whether archived `publishTime` precisely equals public availability time. The pilot can use it as the supplied availability proxy, clearly stated.
