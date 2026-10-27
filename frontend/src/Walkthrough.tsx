import { useEffect, useState } from 'react'

interface Step {
  title: string
  action: string
  expect: string
  target: string
  decisionDate?: string
}

// The screen actions of docs/delivery/video-script.md, each paired with the
// result that docs/delivery/manual-testing.md (sections C and D) expects.
const STEPS: Step[] = [
  {
    title: 'Set the decision date',
    action:
      'Set the date bar to 15 January 2026, the decision date for the walkthrough.',
    expect: 'The date bar reads 15 January 2026, and both views update.',
    target: 'top',
    decisionDate: '2026-01-15',
  },
  {
    title: 'The forecast known at the cutoff',
    action:
      'This view shows the forecast available at 09:00 London time on 15 January, for delivery on 16 January.',
    expect:
      'The decision cutoff is 15 January 2026 at 09:00, and the delivery date is 16 January 2026.',
    target: 'forecast',
  },
  {
    title: 'Hover the forecast line',
    action:
      'Hover a point on the line. Each point shows the forecast, when it was published and how old it was at the cutoff.',
    expect:
      'About 24 points. The tooltip gives the MW value and the publication time.',
    target: 'forecast-chart',
  },
  {
    title: 'Check the data quality',
    action:
      'Read the data-quality summary. A missing or conflicting value appears as a gap, never as zero.',
    expect:
      '24 of 24 hourly targets have a usable forecast, with 0 missing, conflicting or invalid.',
    target: 'quality',
  },
  {
    title: 'Hindsight accuracy for 15 January',
    action:
      'This section uses the actual generation that happened afterwards, so it is labelled hindsight. The teal line is the forecast and the dark line is the actual.',
    expect:
      'MAE about 810 MW, bias about +349 MW (overforecast), RMSE about 970 MW.',
    target: 'accuracy',
  },
  {
    title: 'Select 18 January in the strip',
    action:
      'Select the 18 January column in the January strip. Both views move to that date.',
    expect:
      'Bias is about −684 MW, underforecast, and both views show 18 January.',
    target: 'strip',
    decisionDate: '2026-01-18',
  },
  {
    title: 'Select 27 January, the furthest day',
    action: 'Select 27 January, the decision with the largest miss.',
    expect: 'MAE about 5,329 MW, with a positive bias: overforecast.',
    target: 'metrics',
    decisionDate: '2026-01-27',
  },
  {
    title: 'Read the January figures',
    action:
      'Read the All January line under each card. These pool every matched hourly error, not an average of daily scores.',
    expect:
      '744 matched hourly pairs across January. The January bias is about +1,746 MW.',
    target: 'metrics',
  },
  {
    title: 'Limits and provenance',
    action:
      'Read the limits in the About section, then open the snapshot details.',
    expect:
      'Actuals are the latest retrieved values, not final settlement data. Each dataset shows its SHA-256 hash.',
    target: 'about',
  },
]

const AUTO_PLAY_MS = 8000
const SPOTLIGHT_MS = 2000

export default function Walkthrough({
  onSelectDate,
  onClose,
}: {
  onSelectDate: (decisionDate: string) => void
  onClose: () => void
}) {
  const [index, setIndex] = useState(0)
  const [playing, setPlaying] = useState(false)
  const step = STEPS[index]

  useEffect(() => {
    const { decisionDate, target } = STEPS[index]
    if (decisionDate) onSelectDate(decisionDate)
    const element = document.getElementById(target)
    const reduceMotion = window.matchMedia(
      '(prefers-reduced-motion: reduce)',
    ).matches
    element?.scrollIntoView({
      behavior: reduceMotion ? 'auto' : 'smooth',
      block: 'start',
    })
    element?.classList.add('spotlight')
    const timer = window.setTimeout(
      () => element?.classList.remove('spotlight'),
      SPOTLIGHT_MS,
    )
    return () => {
      window.clearTimeout(timer)
      element?.classList.remove('spotlight')
    }
  }, [index, onSelectDate])

  const atEnd = index === STEPS.length - 1
  const autoPlaying = playing && !atEnd

  useEffect(() => {
    if (!autoPlaying) return
    const timer = window.setTimeout(() => setIndex((i) => i + 1), AUTO_PLAY_MS)
    return () => window.clearTimeout(timer)
  }, [autoPlaying, index])

  return (
    <section className="walkthrough" aria-label="Walkthrough">
      <div className="walkthrough-head">
        <p className="walkthrough-count">
          Step {index + 1} of {STEPS.length}
        </p>
        <button type="button" className="walkthrough-close" onClick={onClose}>
          Close
        </button>
      </div>
      <div className="walkthrough-progress" aria-hidden="true">
        <span style={{ width: `${((index + 1) / STEPS.length) * 100}%` }} />
      </div>
      <div aria-live="polite">
        <h3>{step.title}</h3>
        <p className="walkthrough-text">{step.action}</p>
        <p className="walkthrough-text walkthrough-expect">
          <span>Expect:</span> {step.expect}
        </p>
      </div>
      <div className="walkthrough-controls">
        <button
          type="button"
          onClick={() => {
            setPlaying(false)
            setIndex((i) => i - 1)
          }}
          disabled={index === 0}
        >
          Previous
        </button>
        <button
          type="button"
          onClick={() => setPlaying(!autoPlaying)}
          disabled={atEnd}
        >
          {autoPlaying ? 'Pause' : 'Auto-play'}
        </button>
        <button
          type="button"
          className="primary"
          onClick={() => {
            setPlaying(false)
            setIndex((i) => i + 1)
          }}
          disabled={atEnd}
        >
          Next
        </button>
      </div>
    </section>
  )
}
