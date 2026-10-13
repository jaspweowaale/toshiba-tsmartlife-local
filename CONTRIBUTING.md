# Contributing

This is a developer preview of a small, intentionally narrow project —
see the README's preview banner before anything else.

## Install / run the CLI

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest tests/            # should be fully offline, no network needed
toshiba-tsmartlife-onboard --help
```

Requires Python 3.12+ (the upstream `midea-lan` dependency uses newer
generic-class syntax that older Pythons can't parse).

## What this project does and does not do

**Does**: given the TSmartLife "app-level" cloud constants (see
`docs/TOKEN_ONBOARDING.md` — you likely don't have these; that's the
project's one open problem, not a bug) and your own TSmartLife account,
logs in once and retrieves your specific appliance's local LAN
`token`/`key`, for you to paste into the existing `midea_ac_lan` Home
Assistant integration.

**Does not**: implement any LAN protocol code, create any Home Assistant
entities, run as a Home Assistant integration itself, store your
password or the resulting token/key anywhere persistent (unless you
explicitly pass `--output-file`), or solve the app-level-constant problem
for you.

## Supported model

Only verified against: Toshiba `GR-RF900WI-PMV(06)-MG`, Vietnam market,
TSmartLife app, Midea device type `0xCA`, protocol V3. See
`docs/KNOWN_LIMITATIONS.md` for exactly what is and isn't proven even on
that one model.

## Reporting another model that works

If you run this successfully against a *different* Toshiba model, market,
or appliance category (e.g. the TSmartLife-paired washing machine
mentioned in
[upstream issue #364](https://github.com/wuwentao/midea_ac_lan/issues/364)),
please open an issue — this is genuinely useful and will be used to widen
the README's "Status" table. Don't assume it's obvious or not worth
reporting; a negative/partial result ("ran, but door sensors didn't work")
is also useful, not just a full success.

### What to include

- The exact model number (printed inside the appliance door, or in the
  TSmartLife app's Device Information screen) and market/country.
- Whether the same built-in 4 app-level constants worked as-is, or you
  needed your own different values (do **not** paste the actual values
  into the issue — see "Redacting personal identifiers" below).
- Which entities you confirmed working, and which didn't (see "Reporting
  unsupported sensor fields" below) — exact entity names, e.g.
  `freezer_actual_temp`, not a vague "temperatures worked."
- The Midea device type (`0xCA`, or whatever `python -m midealan.cli
  discover` reports for your appliance) and protocol version, if
  different from this project's tested `0xCA`/V3.

### Redacting personal identifiers

Before posting anything (an issue, a log excerpt, a screenshot), remove:

- Your account email/username and password.
- Your appliance's full serial number and its numeric device ID (the
  first few/last few characters are fine if you want to show the
  *format*, e.g. for confirming a device-type byte, but not the whole
  value).
- Your home's public/local IP address.
- The LAN `token`/`key` pair this project's CLI prints — these are
  specific to your appliance; never share them anywhere, including here.

If you're not sure whether something is safe to post, leave it out and
describe it instead (e.g. "a 24-character hex serial number" rather than
the actual string).

### Reporting unsupported/sentinel sensor fields

If an entity exists in `midea_ac_lan`'s generic 0xCA table but never
reports a real value on your unit (stays `unknown`/`unavailable`, or
reports an implausible constant), that's useful to report too — see
[`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md) for the pattern
this project already found on its one tested unit (`humidity`,
`electronic_smell`, `right_flex_zone_*`). Include:
- The entity's exact name.
- How long you observed it (a single `unknown` right after setup is less
  conclusive than days of consistent `unknown`/a constant value).
- Whether it's listed as a real feature in your appliance's own manual —
  that distinguishes "not implemented on this model" from "name exists in
  the generic table but genuinely doesn't apply to this unit."

### Submitting a compatibility improvement

Two different kinds of change end up looking similar but belong in
different places:

- **A documentation-only update** (adding your confirmed-working model
  to this project's README "Status" section, or a note in
  `docs/KNOWN_LIMITATIONS.md`) belongs **here**, in this repository — open
  a PR against this project.
- **An actual protocol/entity-decoding change** (e.g. your model needs a
  new field decoded, or a different device-type byte handled) belongs
  **upstream**, in [`midea-lan`](https://github.com/wuwentao/midea-lan)
  or [`midea_ac_lan`](https://github.com/wuwentao/midea_ac_lan) — this
  project has no protocol code of its own to change (see
  `docs/ARCHITECTURE.md`). Open that PR/issue against the upstream repo
  instead, and feel free to link back here for context.

If you're unsure which bucket your change falls into, open an issue here
first and ask — that's cheaper than guessing wrong.

## Contributing safely

- **Never commit real credentials, device IDs, serial numbers, IP
  addresses, or app-level constants** — not even "just for this branch,
  I'll remove it later." Git history is effectively permanent once
  pushed. Use the placeholder patterns already in the examples/tests.
- Run the secret-scan pattern used before every release of this project
  (see `docs/PUBLICATION_READINESS.md` for the exact commands used) on
  your own branch before opening a PR.
- If you're touching `onboard.py`, keep every new failure path returning
  a clean `OnboardingError` message — no raw tracebacks reaching the
  user (see the existing exception-wrapping pattern).
- Don't broaden scope into reimplementing the LAN protocol or a full HA
  integration in this repo — see `docs/ARCHITECTURE.md` for why that's a
  deliberate non-goal here. Protocol-level contributions belong upstream,
  in `midea-lan`/`midea_ac_lan`.
- If your change affects what's claimed to work, update `README.md`'s
  status table and `docs/KNOWN_LIMITATIONS.md` in the same PR — don't let
  claims and reality drift apart.

## Privacy/security expectations

See `docs/SECURITY_AND_PRIVACY.md` and `docs/APP_CREDENTIAL_SECURITY.md`.
Short version: your password and the app-level constants never leave
your own machine except to Midea's own cloud login endpoint; the
resulting per-appliance token/key are yours and this project never
transmits them anywhere.

## Upstream attribution

This project depends on, but does not fork or copy,
[`midea-lan`](https://github.com/wuwentao/midea-lan) (MIT, © 2026 Wentao
Wu, © 2021 George Zhao), and recommends
[`midea_ac_lan`](https://github.com/wuwentao/midea_ac_lan) for the actual
Home Assistant integration. Full statement: `NOTICE.md`.
