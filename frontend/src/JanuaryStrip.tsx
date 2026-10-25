import type { DailyAccuracy } from './api'
import { formatCalendarDate } from './time'

const signedMw = new Intl.NumberFormat('en-GB', {
  maximumFractionDigits: 0,
  signDisplay: 'exceptZero',
})

function describe(day: DailyAccuracy): string {
  const { bias } = day.metrics
  const date = formatCalendarDate(day.decisionDate)
  if (bias === null) return `${date} decision: insufficient data`
  const direction =
    bias > 0 ? ', overforecast' : bias < 0 ? ', underforecast' : ''
  return `${date} decision: bias ${signedMw.format(bias)} MW${direction}`
}

export default function JanuaryStrip({
  days,
  decisionDate,
  onSelect,
}: {
  days: DailyAccuracy[]
  decisionDate: string
  onSelect: (decisionDate: string) => void
}) {
  const largest = Math.max(1, ...days.map((d) => Math.abs(d.metrics.bias ?? 0)))
  return (
    <figure className="strip">
      <figcaption>
        <h3>Daily bias across January</h3>
        <p className="note">
          Each column is one decision date. Bars above the line were
          overforecast, below were underforecast. Select a column to inspect
          that day.
        </p>
      </figcaption>
      <div className="strip-days">
        {days.map((day) => {
          const bias = day.metrics.bias
          const height = bias === null ? 0 : (Math.abs(bias) / largest) * 100
          return (
            <button
              key={day.decisionDate}
              type="button"
              className="strip-day"
              aria-pressed={day.decisionDate === decisionDate}
              aria-label={describe(day)}
              title={describe(day)}
              onClick={() => onSelect(day.decisionDate)}
            >
              <span className="strip-half">
                {bias !== null && bias > 0 && (
                  <span className="strip-bar over" style={{ height: `${height}%` }} />
                )}
              </span>
              <span className="strip-half">
                {bias !== null && bias < 0 && (
                  <span className="strip-bar under" style={{ height: `${height}%` }} />
                )}
                {bias === null && <span className="strip-none">–</span>}
              </span>
              <span className="strip-label">{Number(day.decisionDate.slice(8))}</span>
            </button>
          )
        })}
      </div>
    </figure>
  )
}
