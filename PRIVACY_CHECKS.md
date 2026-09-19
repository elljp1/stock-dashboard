# Public-repository account-number guard

Before every journal or trade-log commit, stage only the intended files, then run:

```sh
python test_sensitive_data.py --staged
```

Stop on failure. Remove sensitive values locally and stage the corrected files
before retrying. Never paste a detected value into a commit, issue, PR, log, or
test fixture. Use synthetic values in tests. Use account aliases or last four
digits only; do not add full brokerage identifiers or credentials to this repo.

The staged check reads Git's index, so redacting only the working copy is not
enough. Agents and human contributors must run it before committing; it is not
an automatically installed local hook and GitHub's web editor does not run it.
Run the working-copy tests locally before any browser upload.

The refresh workflow also checks current journal files before rebuilding and
the index before its bot commit. CI runs after a push: it can stop a build but
cannot prevent the initial public Git exposure. This narrow numeric-identifier
guard is not a comprehensive secret/PII scanner. Keep sensitive financial data
out of public repositories even when the tests pass.

This change does not scrub old commits, rotate credentials, change repository
visibility, change forecasts, or change trading/risk rules. Historical removal
requires a separate coordinated plan and authorization.
