import { useState } from 'react'
import AccuracyView from './AccuracyView'
import DecisionPicker from './DecisionPicker'
import ForecastView from './ForecastView'
import SnapshotProvenance from './SnapshotProvenance'
import { DECISION_DATES } from './time'
import Walkthrough from './Walkthrough'

function Mark() {
  return (
    <svg className="mark" width="20" height="20" viewBox="0 0 20 20" aria-hidden="true">
      <path d="M10 10C7.6 7.4 7.4 3.6 10 1.2c2.6 2.4 2.4 6.2 0 8.8z" />
      <path
        d="M10 10C7.6 7.4 7.4 3.6 10 1.2c2.6 2.4 2.4 6.2 0 8.8z"
        transform="rotate(120 10 10)"
      />
      <path
        d="M10 10C7.6 7.4 7.4 3.6 10 1.2c2.6 2.4 2.4 6.2 0 8.8z"
        transform="rotate(240 10 10)"
      />
    </svg>
  )
}

export default function App() {
  const [decisionDate, setDecisionDate] = useState(DECISION_DATES[0])
  const [walkthroughOpen, setWalkthroughOpen] = useState(false)
  return (
    <div className="frame">
      <div className="topbar">
        <p className="brand">
          <Mark />
          Elexon GB wind · January 2026
        </p>
        {!walkthroughOpen && (
          <button
            type="button"
            className="walkthrough-start"
            onClick={() => setWalkthroughOpen(true)}
          >
            Start walkthrough
          </button>
        )}
      </div>
      <main className="sheet">
        <div className="sheet-inner">
          <header id="top" className="title-row">
            <h1>Wind Procurement Pilot</h1>
            <p>
              Historical view of Elexon GB wind forecasts available for day-ahead
              purchase decisions in January 2026, and how accurate they turned out
              to be.
            </p>
          </header>
          <div className="toolbar">
            <DecisionPicker value={decisionDate} onChange={setDecisionDate} />
          </div>
          <ForecastView decisionDate={decisionDate} />
          <AccuracyView
            decisionDate={decisionDate}
            onDecisionDateChange={setDecisionDate}
          />
          <section id="about" className="view">
            <h2>About the data</h2>
            <ul>
              <li>
                Values are Elexon reported GB wind generation in MW. Elexon covers
                wind farms visible to the system operator through operational
                metering, not every UK wind generator or a customer portfolio.
              </li>
              <li>
                Forecasts (WINDFOR) target each hour, while actual generation
                (FUELHH) is reported every half hour. Accuracy comparisons use only
                identical target times.
              </li>
            </ul>
            <SnapshotProvenance />
          </section>
        </div>
      </main>
      {walkthroughOpen && (
        <Walkthrough
          onSelectDate={setDecisionDate}
          onClose={() => setWalkthroughOpen(false)}
        />
      )}
    </div>
  )
}
