import AccuracyView from './AccuracyView'
import ForecastView from './ForecastView'
import SnapshotProvenance from './SnapshotProvenance'

export default function App() {
  return (
    <main>
      <header>
        <h1>Wind Procurement Pilot</h1>
        <p>
          Historical view of Elexon GB wind forecasts available for day-ahead
          purchase decisions in January 2026, and how accurate they turned out
          to be.
        </p>
      </header>
      <ForecastView />
      <AccuracyView />
      <section>
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
      </section>
      <SnapshotProvenance />
    </main>
  )
}
