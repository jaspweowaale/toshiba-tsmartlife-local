# Publication readiness record

Recorded before this repository was first made public, as the explicit
pre-publication checklist required for this project. See the dated
follow-up round below for the built-in-default-credentials commit.

## Follow-up round — built-in default credentials + device discovery

This round adds the maintainer-approved built-in "TSmartLife Vietnam"
default (`src/toshiba_tsmartlife_local/vietnam_defaults.py`) and
interactive multi-appliance selection. This is the **first** commit in
this repository's history to contain a real value of any kind — recorded
here explicitly rather than silently, since it changes the "no real
credential in this repo" claim made in the original scan below for all
prior commits (which remains true for those commits).

**Secrets scan — PASSED, two independent methods, scoped to this round's
actual diff**:
1. **Exact-value check** against both restricted source files (the
   app-level config and, defensively, the unrelated LAN-credentials
   file): the 4 approved values (`app_id`, `app_key`, `iot_key`,
   `hmac_key`) are present **exactly once each, only in
   `vietnam_defaults.py`, nowhere else** (not in any other file, not in
   any doc). The LAN token/key, the numeric device ID, and the full
   unique appliance serial number are **absent everywhere** in the diff —
   checked value-for-value, not just by pattern.
2. **Generic heuristic check** (same method as the original scan below:
   24+-character hex/base64-looking strings) across the same diff: 68
   matches, all manually reviewed — all are Python identifiers, test
   names, file paths, or the one deliberate fake test password already
   reviewed in `test_onboard.py`, **except one**, which re-identified the
   same already-approved `app_key` in its correct, expected location
   (confirmed by direct line lookup, not assumed).
3. A false positive from an earlier, broader scan pass (checking full
   file contents instead of only the actual diff) flagged the
   already-published, pre-existing "Internal model code: `310A079W`"
   README line — confirmed via `git diff README.md` to be **unchanged,
   pre-existing content from the already-published commit `a1e3c84`**,
   not part of this round's diff. Documented here so the false-positive
   investigation itself is on the record, not silently discarded.

**Tests — PASSED**: 36/36 (up from 26 — 10 new, covering built-in-default
precedence, multi-appliance selection, and secure-output/no-password-
echoed verification).

**Lint — PASSED**: `ruff check .`, all checks passed (one `noqa`-directive
nit found and fixed before this record was written).

**Docs updated to stay consistent with shipping real values**:
`APP_CREDENTIAL_SECURITY.md`'s "Responsible recommendation" section
(previously said no real value was in the repo and recommended a private
channel over a public commit) was rewritten to record the maintainer's
actual decision and that the private-channel alternative was consciously
not the path taken. `TOKEN_ONBOARDING.md` and `USER_GUIDE.md`'s
"blocked" framing for layer 2 was replaced with the resolved, built-in-
default state.

## Original scan — before first publication

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
