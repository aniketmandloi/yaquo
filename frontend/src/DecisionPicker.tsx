import { DECISION_DATES, formatCalendarDate } from './time'

export default function DecisionPicker({
  value,
  onChange,
}: {
  value: string
  onChange: (decisionDate: string) => void
}) {
  const index = DECISION_DATES.indexOf(value)
  return (
    <div className="picker" role="group" aria-label="Decision date">
      <button
        type="button"
        onClick={() => onChange(DECISION_DATES[index - 1])}
        disabled={index === 0}
        aria-label="Previous decision date"
      >
        ‹
      </button>
      <label>
        <span className="picker-label">Decision date</span>
        <select value={value} onChange={(e) => onChange(e.target.value)}>
          {DECISION_DATES.map((d) => (
            <option key={d} value={d}>
              {formatCalendarDate(d)}
            </option>
          ))}
        </select>
      </label>
      <button
        type="button"
        onClick={() => onChange(DECISION_DATES[index + 1])}
        disabled={index === DECISION_DATES.length - 1}
        aria-label="Next decision date"
      >
        ›
      </button>
    </div>
  )
}
