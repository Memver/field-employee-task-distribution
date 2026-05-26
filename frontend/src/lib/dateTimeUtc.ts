/** datetime-local value (YYYY-MM-DDTHH:mm) interpreted as UTC wall time */
export function toDateTimeLocalUtc(iso: string | null | undefined): string {
  if (!iso) {
    return ""
  }
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) {
    return ""
  }
  const pad = (n: number) => String(n).padStart(2, "0")
  return `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())}T${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`
}

export function fromDateTimeLocalToUtcIso(local: string): string {
  if (!local) {
    return ""
  }
  const [datePart, timePart] = local.split("T")
  if (!datePart || !timePart) {
    return ""
  }
  const [year, month, day] = datePart.split("-").map(Number)
  const [hour, minute] = timePart.split(":").map(Number)
  if (
    [year, month, day, hour, minute].some((part) => Number.isNaN(part))
  ) {
    return ""
  }
  return new Date(Date.UTC(year, month - 1, day, hour, minute, 0)).toISOString()
}
