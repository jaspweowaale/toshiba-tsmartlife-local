# toshiba-tsmartlife-local

> ## ⚠ DEVELOPER PREVIEW
> This is an early, unofficial, independent developer preview — not a
> finished product, not an official release, and **not affiliated with,
> endorsed by, or supported by Toshiba or Midea** in any way. It uses
> the existing open-source Midea LAN / Home Assistant integration
> ([`midea_ac_lan`](https://github.com/wuwentao/midea_ac_lan)) for all
> actual device communication — this project only helps obtain the one
> piece of information that integration needs for a TSmartLife-paired
> appliance. **Independent onboarding is now solved for this one app
> variant**: this project ships a built-in default for the shared
> TSmartLife app-level configuration (see
> [`docs/APP_CREDENTIAL_SECURITY.md`](docs/APP_CREDENTIAL_SECURITY.md) for
> exactly what that is, why it's safe to ship, and what it is *not* —
> it is not your account, your appliance, or your password). You can
> still override it with your own values for a different app
> variant/market via `--config-file`/env vars — see
> [`docs/TOKEN_ONBOARDING.md`](docs/TOKEN_ONBOARDING.md).
>
> **This project does NOT**: claim support for any Toshiba model other
> than the one named below, claim a fully cloud-free *initial* pairing
> (a one-time cloud login by **you**, with **your own account**, is
> still required to obtain your specific appliance's LAN token/key — see
> the session-displacement warning under [Usage](#usage) before you run
> it), provide automatic/bundled *appliance-specific* token extraction,
> or implement a complete standalone Home Assistant integration (it
> deliberately reuses the existing one).

A small, focused **onboarding helper** that, once you have the
information in `TOKEN_ONBOARDING.md`, gets a Toshiba TSmartLife
("oversea" app, `com.midea.ai.toshiba.oversea.inhouse`) refrigerator's
local LAN token/key so that **temperature and door monitoring then run
entirely on your home network** via
[Home Assistant](https://www.home-assistant.io/) and the existing,
already-public `midea_ac_lan` integration — no further cloud contact
after that one-time onboarding step.

**This project does not reimplement the LAN protocol, the Home Assistant
integration, or the entity table.** `midea_ac_lan` already supports device
type `0xCA` (this refrigerator family) natively — see
[Architecture](#architecture) below for why duplicating that would be the
wrong move. The one piece that doesn't exist anywhere yet is a
reproducible way to get the *credentials* `midea_ac_lan` needs for a
TSmartLife-paired appliance. That's what this project is.

## Status: developer preview, single model verified

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
pip install -e .
```

That single command is enough: this project's own `pyproject.toml`
already declares `midea-lan` as a dependency via its GitHub URL, so pip
fetches and installs it automatically — no separate install step needed.

Two things worth knowing about that dependency:
- `midea-lan` is not confirmed published to PyPI under that exact name as
  of this writing, which is why it's pinned to a GitHub URL rather than a
  plain package name.
- That URL currently points at **our own fork's branch**
  (`jaspweowaale/midea-lan@feat/tsmartlife-cloud-draft`), not plain
  `wuwentao/midea-lan@main` — the TSmartLife cloud support this project
  needs is still an open, unmerged draft
  ([PR #198](https://github.com/wuwentao/midea-lan/pull/198)); upstream
  `main` alone does not yet include it. See
  [`NOTICE.md`](NOTICE.md) for the full explanation. This will switch back
  to plain upstream once that PR merges.

**For a full platform-by-platform walkthrough (installing Python itself,
creating a virtual environment, Windows/macOS/Linux-specific commands),
see [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) step 1a/4** — this section
assumes you already have Python 3.12+ and pip working.

## Usage

**For a plain, step-by-step walkthrough aimed at an ordinary owner, see
[`docs/USER_GUIDE.md`](docs/USER_GUIDE.md).** This section is the terse
reference version.

The 4 shared app-level constants now have a **built-in default**
("TSmartLife Vietnam" — see
[`docs/APP_CREDENTIAL_SECURITY.md`](docs/APP_CREDENTIAL_SECURITY.md)), so
**you don't need to supply anything for this part** unless you want to
override it (e.g. a different market/app variant). To override, pick
whichever you prefer — any of these always takes priority over the
built-in default:

```bash
# Option A: environment variables (all 4 required together to override)
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

Then just:

```bash
toshiba-tsmartlife-onboard
# --username is optional -- you'll be prompted if you omit it
# --device-sn / --device-id are also optional -- if you omit them and
# your account has more than one appliance, you'll see a numbered list
# to pick from interactively; with exactly one appliance, it's used
# automatically, no prompt needed
```

> **⚠ Before you run this**: logging in here uses **your own real
> TSmartLife account** (never stored). A fresh cloud login is known to
> momentarily displace the official TSmartLife app's own session on your
> phone — you may see it show logged-out or need to re-open it
> afterward. This is harmless and temporary, but you should know about it
> in advance rather than be surprised by it.

This prompts for your email (if not given) and password (always hidden,
never a plain CLI argument or logged), logs in to the TSmartLife cloud
**once**, lets you pick your appliance if needed, retrieves its LAN
`token`/`key`, and prints them. Add `--output-file path/to/result.json` to
also save them to a file created with owner-only permissions (POSIX
systems). It does not store your password anywhere, and every expected
failure (missing config, wrong password, network error, appliance not
found) produces a plain-language message — not a raw Python traceback.
Paste the resulting `token`/`key` into your Home Assistant integration's
"Configure manually" step (see `docs/USER_GUIDE.md` for the full HA-side
walkthrough).

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
- [`docs/APP_CREDENTIAL_SECURITY.md`](docs/APP_CREDENTIAL_SECURITY.md) — security/redistribution analysis of the 4 app-level constants
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — how to contribute, including reporting another working model
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
