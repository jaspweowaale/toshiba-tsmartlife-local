# toshiba-tsmartlife-local

A small, focused **onboarding helper** that gets a Toshiba TSmartLife
("oversea" app, `com.midea.ai.toshiba.oversea.inhouse`) refrigerator's
local LAN token/key so it can run entirely on your home network with
[Home Assistant](https://www.home-assistant.io/), using the existing,
already-public
[`midea_ac_lan`](https://github.com/wuwentao/midea_ac_lan) HACS
integration for everything else.

**This project does not reimplement the LAN protocol, the Home Assistant
integration, or the entity table.** `midea_ac_lan` already supports device
type `0xCA` (this refrigerator family) natively — see
[Architecture](#architecture) below for why duplicating that would be the
wrong move. The one piece that doesn't exist anywhere yet is a
reproducible way to get the *credentials* `midea_ac_lan` needs for a
TSmartLife-paired appliance. That's what this project is.

## Status: experimental, single model verified

Verified against exactly one physical unit:

| | |
|---|---|
| Model | Toshiba `GR-RF900WI-PMV(06)-MG` |
| Market | Vietnam |
| App | TSmartLife ("oversea" variant) |
| Midea device type | `0xCA` (refrigerator) |
| Protocol | LAN V3 |
| Internal model code | `310A079W` |

**Do not assume other Toshiba models, other markets, or other Midea-family
apps work identically.** The device-type/protocol family (`0xCA`) is
shared across many Midea-made refrigerators sold under different brands,
so this *may* generalize — but only this one model/app/market combination
has actually been tested end-to-end.

## What's proven to work (confirmed against a real device)

Read-only, via `midea_ac_lan`, once LAN credentials are configured:

- Refrigerator actual temperature and setpoint
- Freezer actual temperature and setpoint
- Flex-zone actual temperature and setpoint
- Upper-door-group state (binary open/closed)
- Lower-door-group state (binary open/closed)

## What is explicitly NOT claimed as working

- **Humidity** — the integration exposes a `humidity` entity, but on this
  unit it has never returned a real value (see
  [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md) for the exact
  root cause, found in the protocol decoder itself). Do not display this
  on a dashboard as if it works.
- **Individual left/right door sensors** — only two door *groups* (upper,
  lower) have ever been confirmed to report a real state change on this
  unit. A third/fourth distinct door entity exists in the entity table but
  has never fired.
- **Instantaneous power/wattage from the Toshiba LAN protocol itself** —
  no such entity exists in this integration for this device type. If you
  want power monitoring, pair a separate smart plug (see
  [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md)).
- Any other Toshiba refrigerator model, any other market, any other
  Midea-family rebrand of this app.

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full comparison
of 6 candidate architectures. Summary: a dedicated HACS integration (or a
fork of `midea_ac_lan`) would duplicate already-working, upstream-
maintained code for no technical benefit, and would mean yet another
integration for users who likely already have `midea_ac_lan` installed for
other Midea appliances. The actual gap is credential onboarding, so this
project is scoped to exactly that: a standalone Python CLI helper, reusing
the upstream [`midea-lan`](https://github.com/wuwentao/midea-lan) library
(MIT-licensed) as a dependency — not a fork, not copied code.

## Installation

```bash
pip install "midea-lan @ git+https://github.com/wuwentao/midea-lan.git"
pip install -e .
```

(`midea-lan` is not confirmed published to PyPI under that exact name as
of this writing — the git URL form above always works regardless. If it
later ships on PyPI, a plain `pip install midea-lan` will also work.)

## Usage

**For a plain, step-by-step walkthrough aimed at an ordinary owner, see
[`docs/USER_GUIDE.md`](docs/USER_GUIDE.md).** This section is the terse
reference version. See
[`docs/TOKEN_ONBOARDING.md`](docs/TOKEN_ONBOARDING.md) for the one real
blocker this project has **not** solved — read it before assuming this
"just works" for you.

The 4 shared app-level constants (see `TOKEN_ONBOARDING.md`) can be
supplied two ways — pick whichever you prefer:

```bash
# Option A: environment variables
export TSMARTLIFE_APP_ID="..."
export TSMARTLIFE_APP_KEY="..."
export TSMARTLIFE_IOT_KEY="..."
export TSMARTLIFE_HMAC_KEY="..."

# Option B: a local JSON file (never commit it -- .gitignore already
# excludes *.secret/.env/*_restricted/, but this file's name is your
# choice, so name it something .gitignore will actually catch, or add
# your own entry)
#   {"app_id": "...", "app_key": "...", "iot_key": "...", "hmac_key": "..."}
export TSMARTLIFE_CONFIG_FILE=~/.config/tsmartlife/app_config.json
# -- or pass --config-file explicitly each time instead of exporting this
```

Then:

```bash
toshiba-tsmartlife-onboard \
  --device-sn "the-serial-number-printed-inside-your-fridge-door"
  # --username is optional -- you'll be prompted if you omit it
```

This prompts for your email (if not given) and password (always hidden,
never a plain CLI argument or logged), logs in to the TSmartLife cloud
**once**, retrieves your specific appliance's LAN `token`/`key`, and
prints them. Add `--output-file path/to/result.json` to also save them to
a file created with owner-only permissions (POSIX systems). It does not
store your password anywhere, and every expected failure (missing config,
wrong password, network error, appliance not found) produces a plain-
language message — not a raw Python traceback. Paste the resulting
`token`/`key` into your Home Assistant integration's "Configure manually"
step (see `docs/USER_GUIDE.md` for the full HA-side walkthrough).

### Install notes by platform

- **Linux/macOS**: `pip install -e .` inside a virtualenv works as shown
  above. `--output-file`'s owner-only permission restriction (POSIX file
  mode 0600) is applied automatically.
- **Windows**: same `pip install -e .` inside a virtualenv (PowerShell or
  cmd). The POSIX permission step for `--output-file` is skipped
  automatically (Windows ACLs work differently) — the file is still only
  written if you explicitly ask for it; prefer the default terminal-only
  output if that matters to you. Run via `py -m toshiba_tsmartlife_local.onboard`
  or the installed `toshiba-tsmartlife-onboard.exe` console script, same
  arguments either way.

## Documentation

- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — plain step-by-step walkthrough, tested/untested/blocked marked per step
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — why this scope, not a full integration
- [`docs/TOKEN_ONBOARDING.md`](docs/TOKEN_ONBOARDING.md) — the real onboarding story, blockers included
- [`docs/SECURITY_AND_PRIVACY.md`](docs/SECURITY_AND_PRIVACY.md)
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md)
- [`docs/DEVELOPER_GUIDE.md`](docs/DEVELOPER_GUIDE.md) — adding another model/market
- [`docs/KNOWN_LIMITATIONS.md`](docs/KNOWN_LIMITATIONS.md)
- [`examples/`](examples/) — generic Home Assistant config + dashboard YAML (no personal device IDs)

## License and attribution

MIT — see [`LICENSE`](LICENSE). This project depends on, but does not
copy, [`wuwentao/midea-lan`](https://github.com/wuwentao/midea-lan)
(MIT, © 2026 Wentao Wu, © 2021 George Zhao) and recommends
[`wuwentao/midea_ac_lan`](https://github.com/wuwentao/midea_ac_lan) for
the actual Home Assistant integration. See
[`NOTICE.md`](NOTICE.md) for the full attribution statement.
