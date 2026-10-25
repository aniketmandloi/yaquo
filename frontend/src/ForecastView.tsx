import { useEffect, useState } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  type TooltipContentProps,
} from 'recharts'
import { fetchForecast, type DecisionForecast, type ForecastTarget } from './api'
import {
  DECISION_DATES,
  formatAge,
  formatCalendarDate,
  formatLondonDateTime,
  formatLondonTime,
} from './time'

const STATUS_LABELS: Record<ForecastTarget['status'], string> = {
  selected: 'Selected',
  missing: 'Missing: no forecast published by the cutoff',
  conflicting: 'Excluded: conflicting values in the latest publication',
  invalid: 'Excluded: invalid value in the latest publication',
}

type Result = { decisionDate: string } & (
  | { kind: 'error'; message: string }
  | { kind: 'ready'; forecast: DecisionForecast }
)

function TargetTooltip({ active, payload }: TooltipContentProps) {
  const target = payload?.[0]?.payload as ForecastTarget | undefined
  if (!active || !target) return null
  return (
    <div className="tooltip">
      <strong>{formatLondonDateTime(target.startTime)}</strong>
      <div>
        {target.generation === null
          ? STATUS_LABELS[target.status]
          : `${target.generation.toLocaleString('en-GB')} MW`}
      </div>
      {target.publishTime && target.ageMinutes !== null && (
        <div>
          Published {formatLondonDateTime(target.publishTime)} (
          {formatAge(target.ageMinutes)} before cutoff)
        </div>
      )}
    </div>
  )
}

function QualitySummary({ forecast }: { forecast: DecisionForecast }) {
  const { quality } = forecast
  const issues = forecast.targets.filter((t) => t.status !== 'selected')
  return (
    <section>
      <h3>Data quality</h3>
      <p>
        {quality.selected} of {quality.expectedHourlyTargets} hourly targets
        have a usable forecast. Missing: {quality.missing}. Conflicting:{' '}
        {quality.conflicting}. Invalid: {quality.invalid}.
      </p>
      {issues.length > 0 && (
        <ul className="issues">
          {issues.map((t) => (
            <li key={t.startTime}>
              {formatLondonTime(t.startTime)}: {STATUS_LABELS[t.status]}
            </li>
          ))}
        </ul>
      )}
      <p className="note">
        Unavailable targets are shown as gaps, never as zero generation.
      </p>
    </section>
  )
}

function TargetTable({ forecast }: { forecast: DecisionForecast }) {
  return (
    <details>
      <summary>All target values</summary>
      <table>
        <thead>
          <tr>
            <th>Target (London)</th>
            <th>Forecast (MW)</th>
            <th>Published</th>
            <th>Age at cutoff</th>
          </tr>
        </thead>
        <tbody>
          {forecast.targets.map((t) => (
            <tr key={t.startTime}>
              <td>{formatLondonTime(t.startTime)}</td>
              <td>
                {t.generation === null
                  ? STATUS_LABELS[t.status]
                  : t.generation.toLocaleString('en-GB')}
              </td>
              <td>{t.publishTime ? formatLondonDateTime(t.publishTime) : '—'}</td>
              <td>{t.ageMinutes === null ? '—' : formatAge(t.ageMinutes)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </details>
  )
}

function ForecastDetails({ forecast }: { forecast: DecisionForecast }) {
  return (
    <>
      <dl className="facts">
        <div>
          <dt>Decision date</dt>
          <dd>{formatCalendarDate(forecast.decisionDate)}</dd>
        </div>
        <div>
          <dt>Delivery date</dt>
          <dd>{formatCalendarDate(forecast.deliveryDate)}</dd>
        </div>
        <div>
          <dt>Decision cutoff</dt>
          <dd>
            {formatLondonDateTime(forecast.cutoff)} ({forecast.timezone})
          </dd>
        </div>
      </dl>

      <h3>Forecast wind generation for the delivery day ({forecast.unit})</h3>
      <div className="chart">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={forecast.targets} margin={{ left: 16, right: 16 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="startTime"
              tickFormatter={formatLondonTime}
              label={{ value: 'Target time (London)', position: 'insideBottom', offset: -4 }}
              height={48}
            />
            <YAxis
              tickFormatter={(v: number) => v.toLocaleString('en-GB')}
              label={{ value: 'MW', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip content={TargetTooltip} />
            <Line
              type="linear"
              dataKey="generation"
              name="Forecast"
              stroke="var(--accent)"
              strokeWidth={2}
              connectNulls={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <QualitySummary forecast={forecast} />
      <TargetTable forecast={forecast} />
    </>
  )
}

export default function ForecastView() {
  const [decisionDate, setDecisionDate] = useState(DECISION_DATES[0])
  const [result, setResult] = useState<Result | null>(null)
  const state = result?.decisionDate === decisionDate ? result : null

  useEffect(() => {
    let current = true
    fetchForecast(decisionDate)
      .then(
        (forecast) =>
          current && setResult({ decisionDate, kind: 'ready', forecast }),
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
    <section>
      <h2>Day-ahead forecast available at the decision cutoff</h2>
      <p>
        For each target hour, the latest Elexon wind forecast published at or
        before 09:00 London time on the decision date. Later publications are
        never used. The 09:00 cutoff is a pilot assumption, not an exchange
        auction deadline.
      </p>
      <label className="picker">
        Decision date{' '}
        <select
          value={decisionDate}
          onChange={(e) => setDecisionDate(e.target.value)}
        >
          {DECISION_DATES.map((d) => (
            <option key={d} value={d}>
              {formatCalendarDate(d)}
            </option>
          ))}
        </select>
      </label>

      {state === null && <p role="status">Loading forecast…</p>}
      {state?.kind === 'error' && (
        <p role="alert" className="error">
          Could not load the forecast: {state.message}
        </p>
      )}
      {state?.kind === 'ready' && <ForecastDetails forecast={state.forecast} />}
    </section>
  )
}
