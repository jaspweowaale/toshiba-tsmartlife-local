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
  machine as Home Assistant) — Python 3.12+.
- **[BLOCKED, read this before continuing]**: the 4 shared TSmartLife
  "app-level" constants described in step 3. See
  [`TOKEN_ONBOARDING.md`](TOKEN_ONBOARDING.md) for exactly what these are
  and why this project cannot hand them to you — this is the one real gap
  in this whole guide, stated here up front rather than discovered three
  steps in.

## 2. Install the HA-side integration — [TESTED]

Install `midea_ac_lan` via HACS (or, on recent Home Assistant releases,
check Settings → Devices & Services → Add Integration for a built-in
"Midea" integration first — **[UNTESTED by this project]**, reported to
exist since HA 2026.8 but not independently confirmed here; if it's not
there, use HACS). Do not configure a device yet — you need the LAN
token/key from step 4 first.

## 3. Get the 4 TSmartLife app constants — [BLOCKED for most readers]

If you already have these (shared by this project's maintainer, or
recovered independently): continue to step 4. **If you don't have them,
there is currently no documented way to get them yourself** — this is
not this guide glossing over a hard step, it is the actual state of
things. See `TOKEN_ONBOARDING.md`'s "The real blocker" section for the
full explanation and what would need to change.

## 4. Run the onboarding CLI — [TESTED against mocked responses; NOT run against the live cloud this session, per safety rules]

```bash
pip install -e "git+https://github.com/wuwentao/midea-lan.git#egg=midea-lan"
pip install -e .   # from this project's own directory
export TSMARTLIFE_APP_ID=... TSMARTLIFE_APP_KEY=... TSMARTLIFE_IOT_KEY=... TSMARTLIFE_HMAC_KEY=...

toshiba-tsmartlife-onboard --device-sn YOUR_SERIAL_NUMBER
```

Enter your email and password when prompted. On success, it prints one or
more `token`/`key` pairs — copy them.

**What's actually verified here**: the login/appliance-lookup/key-retrieval
*code path* is exercised by 26 passing offline tests against mocked cloud
responses, and the same underlying library calls were confirmed working
against this exact real refrigerator in this project's earlier
development (see the project's `RESUME.md` history). **What's not
verified**: this specific CLI wrapper has not itself been run against the
live TSmartLife cloud end-to-end — doing so this session would have meant
a fresh cloud login, which was explicitly avoided (a fresh login is known
to momentarily displace the official app's own session on your phone —
harmless, but worth knowing in advance, not discovering by surprise).

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
