import { useEffect, useState } from 'react'
import { fetchSnapshot, type SnapshotProvenance as Provenance } from './api'
import { formatLondonDateTime } from './time'

export default function SnapshotProvenance() {
  const [provenance, setProvenance] = useState<Provenance | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchSnapshot()
      .then(setProvenance)
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <section>
      <h2>Snapshot provenance</h2>
      {error && (
        <p role="alert" className="error">
          Could not load snapshot details: {error}
        </p>
      )}
      {provenance && (
        <>
          <p>
            Bundled Elexon responses retrieved{' '}
            {formatLondonDateTime(provenance.retrievedAt)}. The app reads this
            snapshot rather than calling Elexon on each request.
          </p>
          <ul>
            {Object.entries(provenance.datasets).map(([name, d]) => (
              <li key={name}>
                <strong>{name}</strong>: publications from{' '}
                {formatLondonDateTime(d.publishDateTimeFrom)} to{' '}
                {formatLondonDateTime(d.publishDateTimeTo)};{' '}
                {d.storedRecords.toLocaleString('en-GB')} of{' '}
                {d.responseRecords.toLocaleString('en-GB')} records kept.{' '}
                {d.transformation} <a href={d.url}>Source query</a>. SHA-256{' '}
                <code className="hash">{d.storedSha256}</code>
              </li>
            ))}
          </ul>
        </>
      )}
    </section>
  )
}
