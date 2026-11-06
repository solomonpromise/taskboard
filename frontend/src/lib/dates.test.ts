import { describe, expect, it } from "vitest";
import { formatDueDate, localToday } from "./dates";

describe("formatDueDate", () => {
  it("shows the calendar date without shifting it across time zones", () => {
    expect(formatDueDate("2026-11-12")).toBe("12 Nov");
    expect(formatDueDate("2026-01-01")).toBe("1 Jan");
  });
});

describe("localToday", () => {
  it("uses the user's time zone, not UTC", () => {
    const oneAmUtc = new Date(Date.UTC(2026, 10, 13, 1, 0));
    expect(localToday("UTC", oneAmUtc)).toBe("2026-11-13");
    expect(localToday("America/New_York", oneAmUtc)).toBe("2026-11-12");
  });
});
