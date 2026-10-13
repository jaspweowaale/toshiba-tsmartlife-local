# User guide: Toshiba GR-RF900WI-PMV(06)-MG, TSmartLife, Vietnam

A plain walkthrough for an ordinary owner. Each step is marked
**[TESTED]**, **[UNTESTED]**, or **[BLOCKED]** — read those marks, they're
not decoration.

## 0. Is this guide for you?

**[TESTED]** only for the exact model above, bought/registered in
Vietnam, paired to the **TSmartLife** app
(`com.midea.ai.toshiba.oversea.inhouse` — check this is really the app
you use; Toshiba also has unrelated apps for other product lines, e.g.
air conditioners use a different app/cloud entirely and are not covered
here).

**[UNTESTED]** for any other Toshiba refrigerator model, any other
market/country, or TSmartLife-paired devices that aren't this refrigerator
(e.g. the TSmartLife-paired washing machine mentioned in
[upstream issue #364](https://github.com/wuwentao/midea_ac_lan/issues/364)
— same app, different device, not verified here). If you try this on a
different model and it works, please say so (sanitized) in an issue —
that's genuinely useful information this guide doesn't have yet.

## 1. Prerequisites

- Home Assistant, with network access to your refrigerator (same LAN/
  VLAN — a few home networks segment "IoT" devices away from the HA
  server, which looks identical to a credential problem; rule this out
  first if you get stuck later).
- Your TSmartLife account email + password (the one your fridge is
  actually paired to in the app).
- Your appliance's serial number, found inside the fridge door, or in the
  TSmartLife app's Device Information screen.
- A computer to run this project's CLI on (does not need to be the same
  machine as Home Assistant) — **Python 3.12 or newer**, see step 1a
  below if you don't already have it.
- The 4 shared TSmartLife "app-level" constants (see step 3) are now
  **built in by default** — nothing to obtain yourself for this part. See
  [`TOKEN_ONBOARDING.md`](TOKEN_ONBOARDING.md) for exactly what these are
  and why shipping a default for them is considered safe.

## 1a. Install Python 3.12+ — [TESTED pattern, standard tooling]

Skip this if `python3 --version` (macOS/Linux) or `py --version` (Windows)
already reports 3.12 or newer.

- **Windows**: install from
  [python.org/downloads](https://www.python.org/downloads/) or
  `winget install Python.Python.3.12` in PowerShell. During the
  python.org installer, tick **"Add python.exe to PATH"** — this is the
  single most common Windows setup mistake for any Python tool, not just
  this one.
- **macOS**: `brew install python@3.12` (Homebrew), or the official
  installer from python.org. The system-provided `/usr/bin/python3` on
  macOS is often older than 3.12 and should not be relied on here.
- **Linux**: use your distribution's package manager, e.g.
  `sudo apt install python3.12 python3.12-venv` (Debian/Ubuntu),
  `sudo dnf install python3.12` (Fedora), or `pyenv install 3.12` if your
  distro only ships an older version by default.

## 2. Install the HA-side integration — [TESTED]

Install `midea_ac_lan` via HACS (or, on recent Home Assistant releases,
check Settings → Devices & Services → Add Integration for a built-in
"Midea" integration first — **[UNTESTED by this project]**, reported to
exist since HA 2026.8 but not independently confirmed here; if it's not
there, use HACS). Do not configure a device yet — you need the LAN
token/key from step 4 first.

## 3. The 4 TSmartLife app constants — [built in, nothing to do]

This project now ships a built-in default for these (the "TSmartLife
Vietnam" preset — see
[`APP_CREDENTIAL_SECURITY.md`](APP_CREDENTIAL_SECURITY.md) for exactly
what they are and the maintainer's reasoning for shipping them). You do
not need to find or supply these yourself for this app variant. If you're
on a *different* TSmartLife app variant/market and know your own 4
values, you can still override the built-in default — see
`TOKEN_ONBOARDING.md`.

## 4. Install and run the onboarding CLI — [TESTED offline against 36 mocked-response cases; NOT run against the live cloud this session, per safety rules]

First, get this project's own source (clone with `git`, or download and
extract the "Code → Download ZIP" archive from
[the repository page](https://github.com/jaspweowaale/toshiba-tsmartlife-local)
if you don't have `git`), then `cd` into that directory. The commands
below are the same on every platform except how you create/activate the
virtual environment:

**Windows (PowerShell)**:
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
```

**macOS / Linux**:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

`pip install -e .` alone is enough — this project's own `pyproject.toml`
already declares `midea-lan` as a dependency and pip fetches it
automatically from its GitHub repository (currently our own fork's
branch, not upstream directly — see [`NOTICE.md`](../NOTICE.md) for why);
there is no separate `midea-lan` install step.

Then, with the virtual environment still active, run:

```bash
toshiba-tsmartlife-onboard
```

(On Windows, if the bare command isn't found for any reason, the
equivalent is `py -m toshiba_tsmartlife_local.onboard` — same arguments
either way.)

Enter your email and password when prompted. If your account has more
than one appliance, you'll see a numbered list to choose from (with
exactly one appliance, it's used automatically). On success, it prints
one or more `token`/`key` pairs — copy them.

> **⚠ Before you run this**: a fresh cloud login is known to momentarily
> displace the official TSmartLife app's own session on your phone — you
> may see it show logged-out, or need to re-open it afterward. This is
> harmless and temporary, but know about it in advance rather than being
> surprised by it mid-setup.

**What's actually verified here**: the login/appliance-discovery/
selection/key-retrieval *code path* is exercised by 36 passing offline
tests against mocked cloud responses (including the built-in-default
precedence logic and the multi-appliance selection prompt), and the same
underlying library calls were confirmed working against this exact real
refrigerator in this project's earlier development (see the project's
`RESUME.md` history). **What's not verified**: this specific CLI wrapper
has not itself been run against the live TSmartLife cloud end-to-end in
this project's testing — doing so would mean a fresh cloud login, which
has been deliberately avoided in every automated session so far for the
reason boxed above, not because the code path is untested.

## 5. Configure Home Assistant — [TESTED, from earlier development]

In `midea_ac_lan` (or "Midea"): Add Integration → **Configure manually** →
device type `0xCA` → protocol `V3` → your fridge's IP address → the
`token`/`key` from step 4.

## 6. Select which data to show — [TESTED]

In the integration's **Options** (a separate step from initial setup),
tick only:

- `refrigerator_actual_temp`, `refrigerator_setting_temp`
- `freezer_actual_temp`, `freezer_setting_temp`
- `flex_zone_actual_temp`, `flex_zone_setting_temp`
- `refrigerator_door` (this is your fridge's upper door group)
- `freezer_door` (lower door group)

Everything else in the generic entity table for this device type is
either confirmed not meaningful on this model (humidity, a couple of
sentinel-value entities — see `KNOWN_LIMITATIONS.md`) or simply untested.

## 7. Example dashboard — [TESTED pattern, generic file]

See [`../examples/lovelace_dashboard_example.yaml`](../examples/lovelace_dashboard_example.yaml).
Substitute `YOUR_DEVICE_ID` with your own appliance's numeric ID (visible
in each entity's own entity_id once step 6 is done).

## 8. Troubleshooting

See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

## 9. Known limitations

See [`KNOWN_LIMITATIONS.md`](KNOWN_LIMITATIONS.md) — humidity, individual
door detection, and power/wattage are all explicitly **not** claimed as
working, with the reason why for each.

## 10. Security and privacy

See [`SECURITY_AND_PRIVACY.md`](SECURITY_AND_PRIVACY.md).

## 11. Attribution

This guide and the tool it describes depend on, but do not copy,
[`midea-lan`](https://github.com/wuwentao/midea-lan) (MIT, © 2026 Wentao
Wu, © 2021 George Zhao) and recommend
[`midea_ac_lan`](https://github.com/wuwentao/midea_ac_lan) for the actual
Home Assistant integration. Full attribution: [`../NOTICE.md`](../NOTICE.md).
