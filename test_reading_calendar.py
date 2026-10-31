import tempfile
import unittest
from datetime import date
from pathlib import Path

from reading_calendar import calendar_text, fold_line, load_plan


class CalendarTest(unittest.TestCase):
    def load(self, text):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.csv"
            path.write_text(text, encoding="utf-8")
            return load_plan(path)

    def test_leap_day_and_exclusive_end(self):
        entries = self.load("date,passage\n2028-02-29,John 1\n")
        result = calendar_text(entries)
        self.assertIn("DTSTART;VALUE=DATE:20280229\r\n", result)
        self.assertIn("DTEND;VALUE=DATE:20280301\r\n", result)
        self.assertEqual(result.count("BEGIN:VEVENT"), 1)

    def test_weekend_gap_is_preserved(self):
        entries = self.load("date,passage\n2026-11-09,John 2\n2026-11-06,John 1\n")
        self.assertEqual([entry[0] for entry in entries], [date(2026, 11, 6), date(2026, 11, 9)])
        self.assertEqual(calendar_text(entries).count("BEGIN:VEVENT"), 2)

    def test_invalid_input(self):
        for text in ["date,passage\n2026-02-30,John 1\n",
                     "date,passage\n2026-11-02,\n",
                     "date,passage\n9999-12-31,John 1\n",
                     "date,passage\n2026-11-02,John 1\n2026-11-02,John 1\n",
                     "date,passage\n2026-11-02,John 1,extra\n",
                     "date,passage\n", "wrong,header\n"]:
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.load(text)

    def test_escaping_does_not_inject_properties(self):
        entries = self.load('date,passage,notes\n2026-11-02,John 1,"note; comma, slash\\\nATTENDEE:evil"\n')
        result = calendar_text(entries)
        self.assertIn(r"note\; comma\, slash\\\nATTENDEE:evil", result)
        self.assertNotIn("\r\nATTENDEE:", result)

    def test_unicode_folding_roundtrip(self):
        text = "DESCRIPTION:" + "Read \u7ea6\u7ff0\u798f\u97f3 carefully; " * 20
        folded = fold_line(text)
        self.assertTrue(all(len(line.encode("utf-8")) <= 75 for line in folded.split("\r\n")))
        self.assertEqual(folded.replace("\r\n ", ""), text)

    def test_bom_and_stable_event_identity(self):
        entries = self.load("\ufeffdate,passage\n2026-11-02,John 1\n")
        first = [line for line in calendar_text(entries).splitlines() if line.startswith("UID:")]
        second = [line for line in calendar_text(entries).splitlines() if line.startswith("UID:")]
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
