"""Convert a dated reading-plan CSV to all-day iCalendar events, offline."""

import argparse
import csv
import hashlib
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


def escape_text(value):
    return (value.replace("\\", "\\\\").replace("\r\n", "\n")
            .replace("\r", "\n").replace("\n", "\\n")
            .replace(";", "\\;").replace(",", "\\,"))


def fold_line(value):
    """Fold to at most 75 UTF-8 octets without splitting a character."""
    lines = []
    current = ""
    size = 0
    for char in value:
        width = len(char.encode("utf-8"))
        if size + width > 75:
            lines.append(current)
            current, size = " ", 1
        current += char
        size += width
    lines.append(current)
    return "\r\n".join(lines)


def load_plan(path):
    entries = []
    seen = set()
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not {"date", "passage"}.issubset(reader.fieldnames or []):
            raise ValueError("CSV needs date and passage columns; notes is optional")
        for line, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"Row {line}: inconsistent CSV column count")
            raw_date = row["date"].strip()
            passage = row["passage"].strip()
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date) or not passage:
                raise ValueError(f"Row {line}: use YYYY-MM-DD and a nonempty passage")
            try:
                day = date.fromisoformat(raw_date)
                end = day + timedelta(days=1)
            except (ValueError, OverflowError) as error:
                raise ValueError(f"Row {line}: invalid or unsupported date") from error
            key = (day, passage)
            if key in seen:
                raise ValueError(f"Row {line}: duplicate date and passage")
            seen.add(key)
            entries.append((day, end, passage, row.get("notes", "")))
    if not entries:
        raise ValueError("CSV contains no reading rows")
    return sorted(entries, key=lambda entry: (entry[0], entry[2]))


def calendar_text(entries, name="Bible reading"):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
             "PRODID:-//Reading Calendar CSV//EN", "CALSCALE:GREGORIAN",
             "X-WR-CALNAME:" + escape_text(name)]
    for day, end, passage, notes in entries:
        identity = (name + "\0" + day.isoformat() + "\0" + passage).encode("utf-8")
        uid = hashlib.sha256(identity).hexdigest() + "@reading-calendar.local"
        lines.extend(["BEGIN:VEVENT", "UID:" + uid, "DTSTAMP:" + stamp,
                      "DTSTART;VALUE=DATE:" + day.strftime("%Y%m%d"),
                      "DTEND;VALUE=DATE:" + end.strftime("%Y%m%d"),
                      "SUMMARY:" + escape_text("Read " + passage),
                      "TRANSP:TRANSPARENT"])
        if notes:
            lines.append("DESCRIPTION:" + escape_text(notes))
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold_line(line) for line in lines) + "\r\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("ics", type=Path)
    parser.add_argument("--name", default="Bible reading")
    args = parser.parse_args()
    try:
        entries = load_plan(args.csv)
        content = calendar_text(entries, args.name)
        with args.ics.open("x", encoding="utf-8", newline="") as stream:
            stream.write(content)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    print(f"Wrote {len(entries)} all-day events to {args.ics}")


if __name__ == "__main__":
    main()
