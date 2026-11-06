// Due dates are calendar dates ("2026-11-12"), not moments in time (book Chapter 10).
// Format them without converting time zones, so 12 Nov never becomes 11 Nov.

const formatter = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", timeZone: "UTC" });

export function formatDueDate(isoDate: string): string {
  const [year, month, day] = isoDate.split("-").map(Number);
  return formatter.format(new Date(Date.UTC(year, month - 1, day)));
}

// Today's date in the user's own time zone, as YYYY-MM-DD (for the date picker's minimum).
export function localToday(timeZone: string, now: Date = new Date()): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone, year: "numeric", month: "2-digit", day: "2-digit" }).format(now);
}

export function browserTimeZone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
}
