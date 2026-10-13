# Publication readiness record

Recorded before this repository was first made public, as the explicit
pre-publication checklist required for this project.

## Secrets scan — PASSED

Performed against **every tracked file** and **the full `git log --all -p`
history** (not just the current working tree) immediately before
publishing:

- Long hex/base64-looking strings (24+ characters): **none found** in any
  file or any commit diff (the only pattern matches were git's own
  40-character commit-hash header lines, confirmed as a scan artifact,
  not content, by re-checking with those lines excluded).
- The real device ID, LAN IP address, and serial-number prefix used
  during this project's development: **none found**, anywhere in tracked
  files or history.
- `password`/`secret` assigned to a literal value: **none found** other
  than clearly-marked placeholder strings (`test_only_...`, `...`,
  `YOUR_DEVICE_ID`, etc.) already present by design in tests/examples.
- No `.env` file, nor any file matching `*secret*`/`*restricted*`/
  `*credential*`, has ever been tracked in this repository, at any commit.
- Full list of every file ever added across the entire history was
  diffed against the current tree: identical — no file was ever added
  and later removed (which would still leave it recoverable from
  history).

## Tests — PASSED

26/26 tests pass, fully offline, no network access or real credentials
used anywhere in the test suite.

## Lint — PASSED

`ruff check src/ tests/`: all checks passed.

## LICENSE / NOTICE — confirmed present and correct

- `LICENSE`: MIT, this project's own copyright plus the upstream
  `midea-lan` MIT license reproduced for reference (that project's own
  license governs its own source; it is not vendored here).
- `NOTICE.md`: states the dependency relationship to `midea-lan`
  (not forked, not copied), recommends `midea_ac_lan` for the actual Home
  Assistant integration, and states plainly that no private data is
  present in this repository's history.

## README — onboarding limitation prominence confirmed

The README's developer-preview banner (top of file, before any other
content) states plainly that independent onboarding is not yet fully
solved, points to `docs/TOKEN_ONBOARDING.md` for the exact blocker, and
explicitly disclaims: official Toshiba/Midea affiliation, support for
untested models, a fully cloud-free initial pairing, automatic token
extraction, and a complete standalone Home Assistant integration.

## Commits published

- `b85eadb` — Initial project foundation: onboarding CLI, docs, examples
- `140d2d0` — Harden onboarding CLI: config-file support, error handling,
  output-file, user guide
- (this round's commit, see `RESUME.md` for its exact hash) — security
  analysis, publication-readiness fixes, contributor docs

No commit, in this repository's entire history, contains a real
credential, device identifier, or private data of any kind.
