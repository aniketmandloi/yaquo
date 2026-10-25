import { useEffect, useState } from 'react'
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from 'recharts'
import {
  fetchAccuracy,
  type AccuracyCoverage,
  type AccuracyMetrics,
  type AccuracyPair,
  type DecisionAccuracy,
  type TargetStatus,
} from './api'
import JanuaryStrip from './JanuaryStrip'
import {
  formatCalendarDate,
  formatLondonDateTime,
  formatLondonTime,
} from './time'

const AXIS_TICK = { fill: 'var(--muted)', fontSize: 12 }

const STATUS_LABELS: Record<TargetStatus, string> = {
  selected: 'Selected',
  missing: 'Missing',
  conflicting: 'Excluded: conflicting',
  invalid: 'Excluded: invalid',
}

const mw = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 0 })
const signedMw = new Intl.NumberFormat('en-GB', {
  maximumFractionDigits: 0,
  signDisplay: 'exceptZero',
})

type Result = { decisionDate: string } & (
  | { kind: 'error'; message: string }
  | { kind: 'ready'; accuracy: DecisionAccuracy }
)

function value(generation: number | null, status: TargetStatus): string {
  return generation === null ? STATUS_LABELS[status] : `${mw.format(generation)} MW`
}

function PairTooltip({ active, payload }: TooltipContentProps) {
  const pair = payload?.[0]?.payload as AccuracyPair | undefined
  if (!active || !pair) return null
  return (
    <div className="tooltip">
      <strong>{formatLondonDateTime(pair.startTime)}</strong>
      <div>Forecast: {value(pair.forecast, pair.forecastStatus)}</div>
      <div>Actual: {value(pair.actual, pair.actualStatus)}</div>
      <div>
        Error:{' '}
        {pair.error === null ? 'Not scored' : `${signedMw.format(pair.error)} MW`}
      </div>
      {pair.forecastPublishTime && (
        <div>Forecast published {formatLondonDateTime(pair.forecastPublishTime)}</div>
      )}
      {pair.actualPublishTime && (
        <div>Actual published {formatLondonDateTime(pair.actualPublishTime)}</div>
      )}
    </div>
  )
}

function metricText(metric: number | null, signed = false): string {
  if (metric === null) return 'Insufficient data'
  return `${(signed ? signedMw : mw).format(metric)} MW`
}

function biasDirection(bias: number | null): string | null {
  if (bias === null || bias === 0) return null
  return bias > 0 ? 'overforecast' : 'underforecast'
}

function MetricCards({
  day,
  period,
}: {
  day: AccuracyMetrics
  period: AccuracyMetrics
}) {
  const cards = [
    {
      name: 'MAE',
      explanation: 'Average size of a miss, ignoring direction.',
      day: metricText(day.mae),
      period: metricText(period.mae),
      direction: null,
    },
    {
      name: 'Bias (mean signed error)',
      explanation:
        'Average forecast minus actual. Positive means wind was overforecast, which can leave a buyer relying on it short.',
      day: metricText(day.bias, true),
      period: metricText(period.bias, true),
      direction: biasDirection(day.bias),
    },
    {
      name: 'RMSE',
      explanation: 'Like MAE, but larger misses count more heavily.',
      day: metricText(day.rmse),
      period: metricText(period.rmse),
      direction: null,
    },
  ]
  return (
    <>
      <div className="metric-cards">
        {cards.map((card) => (
          <div key={card.name} className="metric-card">
            <h4>{card.name}</h4>
            <p className={`metric-value ${card.direction ?? ''}`}>
              {card.day}
              {card.direction && (
                <span className="metric-direction">{card.direction}</span>
              )}
            </p>
            <p className="metric-period">All January: {card.period}</p>
            <p className="note">{card.explanation}</p>
          </div>
        ))}
      </div>
      <p className="note">
        Matched pairs: {day.matchedPairs} on this delivery day,{' '}
        {period.matchedPairs} across January. Pairs are hourly targets with
        both a usable forecast and actual.
      </p>
    </>
  )
}

function CoverageSummary({
  title,
  coverage,
}: {
  title: string
  coverage: AccuracyCoverage
}) {
  const { forecast, actualAtHourlyTargets: actual } = coverage
  const timeline = coverage.halfHourActualTimeline
  return (
    <div>
      <h4>{title}</h4>
      <ul>
        <li>
          {coverage.matchedPairs} of {coverage.hourlyForecastTargets} hourly
          forecast targets matched to an actual at the identical time.
        </li>
        <li>
          Forecasts at those hours: {forecast.selected} usable,{' '}
          {forecast.missing} missing, {forecast.conflicting} conflicting,{' '}
          {forecast.invalid} invalid.
        </li>
        <li>
          Actuals at those hours: {actual.selected} usable, {actual.missing}{' '}
          missing, {actual.conflicting} conflicting, {actual.invalid} invalid.
        </li>
        <li>
          Half-hour actual timeline: {timeline.selected} of {timeline.targets}{' '}
          usable ({timeline.missing} missing, {timeline.conflicting}{' '}
          conflicting, {timeline.invalid} invalid).
        </li>
      </ul>
    </div>
  )
}

function PairTable({ pairs }: { pairs: AccuracyPair[] }) {
  return (
    <details>
      <summary>All hourly comparisons</summary>
      <table>
        <thead>
          <tr>
            <th>Target (London)</th>
            <th>Forecast (MW)</th>
            <th>Actual (MW)</th>
            <th>Error (MW)</th>
            <th>Forecast published</th>
            <th>Actual published</th>
          </tr>
        </thead>
        <tbody>
          {pairs.map((p) => (
            <tr key={p.startTime}>
              <td>{formatLondonTime(p.startTime)}</td>
              <td>
                {p.forecast === null
                  ? STATUS_LABELS[p.forecastStatus]
                  : mw.format(p.forecast)}
              </td>
              <td>
                {p.actual === null
                  ? STATUS_LABELS[p.actualStatus]
                  : mw.format(p.actual)}
              </td>
              <td>{p.error === null ? 'Not scored' : signedMw.format(p.error)}</td>
              <td>
                {p.forecastPublishTime
                  ? formatLondonDateTime(p.forecastPublishTime)
                  : '—'}
              </td>
              <td>
                {p.actualPublishTime
                  ? formatLondonDateTime(p.actualPublishTime)
                  : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </details>
  )
}

function AccuracyDetails({
  accuracy,
  onDecisionDateChange,
}: {
  accuracy: DecisionAccuracy
  onDecisionDateChange: (decisionDate: string) => void
}) {
  const { day, period } = accuracy
  return (
    <>
      <dl className="facts">
        <div>
          <dt>Decision date</dt>
          <dd>{formatCalendarDate(accuracy.decisionDate)}</dd>
        </div>
        <div>
          <dt>Delivery date</dt>
          <dd>{formatCalendarDate(accuracy.deliveryDate)}</dd>
        </div>
        <div>
          <dt>Forecasts selected at</dt>
          <dd>
            {formatLondonDateTime(accuracy.cutoff)} ({accuracy.timezone})
          </dd>
        </div>
      </dl>

      <JanuaryStrip
        days={period.days}
        decisionDate={accuracy.decisionDate}
        onSelect={onDecisionDateChange}
      />

      <h3>Forecast and actual wind generation ({accuracy.unit})</h3>
      <div className="chart">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={day.pairs} margin={{ left: 16, right: 16 }}>
            <CartesianGrid vertical={false} stroke="var(--line)" />
            <XAxis
              dataKey="startTime"
              tick={AXIS_TICK}
              stroke="var(--line)"
              tickFormatter={formatLondonTime}
              label={{
                value: 'Target time (London)',
                position: 'insideBottom',
                offset: -4,
                fill: 'var(--muted)',
              }}
              height={48}
            />
            <YAxis
              tick={AXIS_TICK}
              stroke="var(--line)"
              tickFormatter={(v: number) => mw.format(v)}
              label={{ value: 'MW', angle: -90, position: 'insideLeft', fill: 'var(--muted)' }}
            />
            <Tooltip content={PairTooltip} />
            <Legend verticalAlign="top" wrapperStyle={{ fontSize: 14 }} />
            <Line
              type="linear"
              dataKey="forecast"
              name="Forecast at cutoff"
              stroke="var(--forecast)"
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
              connectNulls={false}
              isAnimationActive={false}
            />
            <Line
              type="linear"
              dataKey="actual"
              name="Actual (latest retrieved)"
              stroke="var(--actual)"
              strokeWidth={2}
              strokeDasharray="6 3"
              dot={false}
              activeDot={{ r: 4 }}
              connectNulls={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="note">
        Only hourly targets are compared. Half-hour actuals between forecast
        hours are not interpolated or averaged. Unavailable values are gaps,
        never zero.
      </p>

      <h3>Accuracy</h3>
      <MetricCards day={day.metrics} period={period.metrics} />
      <p className="note">
        The January figures pool every matched hourly error from the{' '}
        {formatCalendarDate(period.firstDecisionDate)} to{' '}
        {formatCalendarDate(period.lastDecisionDate)} decisions, each using its
        own 09:00 cutoff. They are not an average of daily scores.
      </p>

      <h3>Coverage</h3>
      <div className="coverage">
        <CoverageSummary title="Selected delivery day" coverage={day.coverage} />
        <CoverageSummary title="All January decisions" coverage={period.coverage} />
      </div>

      <PairTable pairs={day.pairs} />
    </>
  )
}

export default function AccuracyView({
  decisionDate,
  onDecisionDateChange,
}: {
  decisionDate: string
  onDecisionDateChange: (decisionDate: string) => void
}) {
  const [result, setResult] = useState<Result | null>(null)
  // Earlier results stay on screen, dimmed, so the page keeps its height
  // and scroll position while the next date loads.
  const loading = result?.decisionDate !== decisionDate

  useEffect(() => {
    let current = true
    fetchAccuracy(decisionDate)
      .then(
        (accuracy) =>
          current && setResult({ decisionDate, kind: 'ready', accuracy }),
      )
      .catch(
        (error: Error) =>
          current &&
          setResult({ decisionDate, kind: 'error', message: error.message }),
      )
    return () => {
      current = false
    }
  }, [decisionDate])

  return (
    <section className="view hindsight">
      <p className="eyebrow">Hindsight: uses outcomes after delivery</p>
      <h2>Retrospective accuracy against retrieved actuals</h2>
      <p>
        Compares the forecasts available at each decision cutoff with Elexon
        actual generation reported afterwards. These scores use outcomes that
        were not known when the decisions were made: they evaluate past
        forecast performance, not a risk estimate available in early January.
      </p>
      <p className="note">
        Actuals are the latest values retrieved in the snapshot, not final
        settlement data, and later corrections may exist. Scores do not imply
        procurement volumes or financial savings.
      </p>
      {(result === null || (loading && result.kind === 'error')) && (
        <p role="status">Loading accuracy…</p>
      )}
      {!loading && result?.kind === 'error' && (
        <p role="alert" className="error">
          Could not load accuracy: {result.message}
        </p>
      )}
      {result?.kind === 'ready' && (
        <div className="results" aria-busy={loading}>
          <AccuracyDetails
            accuracy={result.accuracy}
            onDecisionDateChange={onDecisionDateChange}
          />
        </div>
      )}
    </section>
  )
}
