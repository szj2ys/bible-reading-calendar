# Reading-plan CSV to calendar

Turn a dated Bible reading schedule into an `.ics` calendar file. The converter runs offline, uses only Python's standard library, and accepts your own passages and notes. It creates all-day events on the dates in your CSV, so a weekday schedule keeps its weekend gaps.

## Quick start

Requires Python 3.9 or later. No install step, account, API key, or network connection is needed after downloading the files.

```console
python reading_calendar.py example.csv reading-plan.ics
python -m unittest -v
```

The example produces five events for 2-6 November 2026. Each event contains a passage label and a brief study prompt. To try a different name:

```console
python reading_calendar.py example.csv group-plan.ics --name "November reading group"
```

Use a new output filename each time: the converter refuses to overwrite existing files. Download the source using GitHub's **Code > Download ZIP**, extract it, and run the commands from that folder.

## Make your own schedule

Create a UTF-8 CSV with `date` and `passage` columns; `notes` is optional. Dates must use `YYYY-MM-DD`. Quote any cell containing commas or line breaks. A spreadsheet's CSV UTF-8 export is suitable.

```csv
date,passage,notes
2026-11-02,John 1,Read the opening paragraph twice.
2026-11-03,John 2,"Observe the people, places, and sequence."
```

The tool sorts dates, rejects duplicate date/passage pairs and invalid dates, and preserves Chinese and other Unicode text. It treats passage labels as text: it does not validate Bible references or generate a reading plan. The dates, passage selection, and notes are yours to check.

If you need to design a schedule first, [TrustBible's free reading-plan generator](https://trustbible.org/en/bible-reading-plan-generator/) offers whole-Bible, Old Testament, or New Testament plans with weekday or everyday reading. Copy your chosen dates and passages into this CSV format. This repository is maintained for TrustBible; the website does not currently provide this converter as a built-in calendar export.

## Import without disturbing your main calendar

Create a separate calendar for your reading plan, then use your calendar application's `.ics` import function. Check the first and last dates and a weekend gap before relying on it. This project does not connect to your account or perform the import.

Calendar applications differ in how they handle repeated imports. Stable event identifiers are included, but duplicate prevention during a second import is not guaranteed. Prefer deleting or replacing the separate imported calendar when you regenerate a schedule. No reminders, timed appointments, recurrence rules, invitations, tracking, or synchronization are added.

## Format and verification

The output uses the all-day `DATE` form from [RFC 5545](https://www.rfc-editor.org/rfc/rfc5545). `DTEND` is the following date because the event end is exclusive. Text escapes commas, semicolons, backslashes, and newlines; long lines fold at UTF-8 character boundaries within 75 octets. The tests cover leap-day rollover, missing/invalid rows, duplicate readings, calendar-property injection, Unicode folding, and stable event IDs.

Verified locally with Python 3.10 and the included example. Import into each calendar vendor's current UI has not been tested. This is a small file converter, not a Bible text corpus, church endorsement, or medical/pastoral advice.

## License

MIT. The sample consists of passage references and original prompts, not reproduced Bible text.
