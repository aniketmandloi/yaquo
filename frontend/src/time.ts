const londonDateTime = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Europe/London',
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  timeZoneName: 'short',
})

const londonTime = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'Europe/London',
  hour: '2-digit',
  minute: '2-digit',
})

const calendarDate = new Intl.DateTimeFormat('en-GB', {
  timeZone: 'UTC',
  weekday: 'short',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})

export function formatLondonDateTime(instant: string): string {
  return londonDateTime.format(new Date(instant))
}

export function formatLondonTime(instant: string): string {
  return londonTime.format(new Date(instant))
}

// Decision and delivery dates are calendar dates, not instants.
export function formatCalendarDate(isoDate: string): string {
  return calendarDate.format(new Date(`${isoDate}T00:00:00Z`))
}

export function formatAge(minutes: number): string {
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  return hours ? `${hours} h ${rest} min` : `${rest} min`
}
