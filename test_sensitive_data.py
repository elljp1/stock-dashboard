"""Targeted account-number regression guard; never print matching values.

Run normally to check public journal files, or with --staged before committing
to check the actual Git index (not a potentially different working copy).
This is not a comprehensive PII/secret scanner and cannot erase Git history.
"""
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LONG_NUMBER = re.compile(r"(?<!\d)(?:\d{8,}|\d{3,}(?:[ -]\d{3,})+)(?!\d)")
ACCOUNT_KEYS = {"account", "accountnumber", "brokerageaccount"}
FILES = ("spread_journal.json", "real_trades.json", "trades_log.json", "SPREAD_JOURNAL.md")


def account_strings(value):
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = re.sub(r"[^a-z]", "", key.lower())
            if normalized in ACCOUNT_KEYS and isinstance(child, (str, int)):
                yield str(child)
            yield from account_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from account_strings(child)


def contains_account_number(name, text):
    candidates = account_strings(json.loads(text)) if name.endswith(".json") else [text]
    return any(sum(c.isdigit() for c in match.group()) >= 8
               for value in candidates for match in LONG_NUMBER.finditer(value))


def check_files(read):
    # Report only a count: source values, JSON parser excerpts, and keys may be sensitive.
    failures = 0
    for name in FILES:
        try:
            failures += bool(contains_account_number(name, read(name)))
        except (OSError, ValueError, subprocess.CalledProcessError):
            failures += 1
    return failures


def read_staged(name):
    return subprocess.run(
        ["git", "show", ":" + name], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
    ).stdout


class SensitiveDataTests(unittest.TestCase):
    def test_public_files(self):
        self.assertEqual(check_files(lambda name: (ROOT / name).read_text(encoding="utf-8")),
                         0, "Public account-number guard failed; inspect locally without logging values")

    def test_synthetic_unmasked_values(self):
        for value in ("123456789", 123456789, "TEST-123-456-789", "123 456 789"):
            for key in ("account", "account_number", "accountNumber", "brokerage-account"):
                text = json.dumps({"trades": [{key: value}]})
                self.assertTrue(contains_account_number("fixture.json", text))

    def test_masked_and_structured_aliases(self):
        for value in ("TEST account", "TEST ••••1234", {"label": "TEST", "last4": "1234"}):
            self.assertFalse(contains_account_number("fixture.json", json.dumps({"account": value})))

    def test_financial_amount_is_not_an_account_identifier(self):
        self.assertFalse(contains_account_number("fixture.json", '{"value": 123456789}'))

    def test_markdown(self):
        self.assertTrue(contains_account_number("fixture.md", "Account: TEST 123456789"))
        self.assertFalse(contains_account_number("fixture.md", "Account: TEST ••••1234"))
        self.assertFalse(contains_account_number("fixture.md", "Review 2026-09-18, balance $11,000"))

    def test_parse_error_fails_closed(self):
        self.assertEqual(check_files(lambda _: "invalid json"), 3)

    def test_missing_file_fails_closed(self):
        def missing(_):
            raise OSError("unavailable")
        self.assertEqual(check_files(missing), len(FILES))


if __name__ == "__main__":
    if sys.argv[1:] == ["--staged"]:
        failed = check_files(read_staged)
        print("Account-number guard: " + ("FAIL (inspect locally; values withheld)" if failed else "PASS"))
        sys.exit(bool(failed))
    unittest.main()
