export type TargetStatus = 'selected' | 'missing' | 'conflicting' | 'invalid'

export interface ForecastTarget {
  startTime: string
  status: TargetStatus
  generation: number | null
  publishTime: string | null
  ageMinutes: number | null
}

export interface DecisionForecast {
  decisionDate: string
  deliveryDate: string
  cutoff: string
  timezone: string
  unit: string
  targets: ForecastTarget[]
  quality: {
    expectedHourlyTargets: number
    selected: number
    missing: number
    conflicting: number
    invalid: number
  }
}

export type StatusCounts = Record<TargetStatus, number>

export interface AccuracyPair {
  startTime: string
  forecast: number | null
  forecastStatus: TargetStatus
  forecastPublishTime: string | null
  actual: number | null
  actualStatus: TargetStatus
  actualPublishTime: string | null
  error: number | null
}

// Metric values are null when there are no matched pairs.
export interface AccuracyMetrics {
  matchedPairs: number
  mae: number | null
  bias: number | null
  rmse: number | null
}

export interface AccuracyCoverage {
  hourlyForecastTargets: number
  forecast: StatusCounts
  actualAtHourlyTargets: StatusCounts
  matchedPairs: number
  halfHourActualTimeline: StatusCounts & { targets: number }
}

export interface DecisionAccuracy {
  decisionDate: string
  deliveryDate: string
  cutoff: string
  timezone: string
  unit: string
  day: {
    pairs: AccuracyPair[]
    metrics: AccuracyMetrics
    coverage: AccuracyCoverage
  }
  period: {
    firstDecisionDate: string
    lastDecisionDate: string
    metrics: AccuracyMetrics
    coverage: AccuracyCoverage
  }
}

export interface DatasetProvenance {
  file: string
  url: string
  publishDateTimeFrom: string
  publishDateTimeTo: string
  responseSha256: string
  responseRecords: number
  transformation: string
  storedRecords: number
  storedSha256: string
}

export interface SnapshotProvenance {
  retrievedAt: string
  datasets: Record<string, DatasetProvenance>
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const detail = typeof body?.detail === 'string' ? body.detail : null
    throw new Error(detail ?? `Request failed with status ${response.status}`)
  }
  return response.json() as Promise<T>
}

export function fetchForecast(decisionDate: string): Promise<DecisionForecast> {
  const query = new URLSearchParams({ decision_date: decisionDate })
  return getJson(`/api/forecasts?${query}`)
}

export function fetchAccuracy(decisionDate: string): Promise<DecisionAccuracy> {
  const query = new URLSearchParams({ decision_date: decisionDate })
  return getJson(`/api/accuracy?${query}`)
}

export function fetchSnapshot(): Promise<SnapshotProvenance> {
  return getJson('/api/snapshot')
}
