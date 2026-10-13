# Token/key onboarding: what's solved, what isn't

This is the single most important document in this project. Read it
before assuming the CLI "just works" for you.

## The 4 layers, clearly distinguished

1. **TSmartLife account authentication** — your own email + password for
   the TSmartLife app. You already have this. Nothing to solve.
2. **Cloud application configuration** — 4 values (`app_id`, `app_key`,
   `iot_key`, `hmac_key`) that identify the TSmartLife *app itself* to
   Midea's cloud. **These are the same 4 values for every TSmartLife
   installation on earth** — they are not your account's secret, they are
   the app's. **This project now ships them as a built-in default** (the
   "TSmartLife Vietnam" preset) — see "Resolved: built-in default now
   shipped" below for what that does and doesn't mean, and
   [`APP_CREDENTIAL_SECURITY.md`](APP_CREDENTIAL_SECURITY.md) for the full
   classification/reasoning. You only need to care about this layer
   yourself if you're on a *different* app variant/market and want to
   override the default.
3. **Appliance-specific LAN token/key** — unique per physical appliance,
   derived automatically from (1) + (2) via the cloud's `getToken` API.
   Fully automated by this project's CLI once (2) is available.
4. **Local LAN protocol handshake + ongoing local operation** — already
   solved, upstream, by `midea_ac_lan`. Once (3) is configured there, no
   further cloud contact of any kind is required for ongoing use
   (confirmed by direct testing: a fresh `login()` is needed only to
   obtain (3), never again afterward).

## What's reproducible right now, for anyone

Layer 2 is now built in by default, so **the entire process is a single
CLI command with your own account** — nothing to export first:

```bash
toshiba-tsmartlife-onboard --username you@example.com
# --device-sn/--device-id optional -- omit them for an interactive
# numbered pick if your account has more than one appliance
```

This performs layers 1 and 3 automatically — no APK work, no Android
emulator, no reverse engineering, by design. It was built specifically so
an ordinary owner never has to repeat what this project's own development
required (see below).

## Resolved: built-in default now shipped

As of this version, the project's maintainer has reviewed
[`APP_CREDENTIAL_SECURITY.md`](APP_CREDENTIAL_SECURITY.md)'s classification
of the 4 layer-2 values (shared app-wide identifiers, not a per-account or
per-device secret; upstream `midea-lan` already publishes equivalent
constants in plaintext for 5 other clouds with no visible dispute) and
explicitly approved shipping **this project's own already-recovered copy**
of the 4 values as the built-in default (`src/toshiba_tsmartlife_local/
vietnam_defaults.py`). This is a one-time, explicit decision by this
project's maintainer for these specific 4 values — not a change to this
project's general policy on secrets, and not a claim that redistribution
is affirmatively permitted by Midea/Toshiba's terms of service (still
**unresolved**, see below).

**What this does solve**: an ordinary Vietnamese TSmartLife owner on this
app variant no longer needs to do anything at all for layer 2 — it's
already there. **What this does NOT solve or change**:
- Layers 1 (your account) and 3 (your appliance's own LAN token/key) are
  exactly as before — still require your own one-time login, still
  nothing this project stores.
- Whether Midea/Toshiba's ToS actually permits redistributing these 4
  values is still an open, unresearched legal question (no such ToS
  document has been located or read by this project).
- The vendor could rotate these values in a future app update, which
  would break the built-in default for everyone at once — if that
  happens, the historical extraction method below is what would need to
  be repeated (by someone willing to, not a requirement placed on any
  user).
- Support for any *other* TSmartLife app variant/market still requires
  someone to obtain and contribute (or privately use, via override) that
  variant's own 4 values — this project does not claim the Vietnam preset
  works for other variants.

## Background: how these values were originally obtained (historical, not a user-facing blocker anymore)

Layer 2's 4 values are **not published anywhere** — not in Midea's
official developer documentation (which covers a *different*, formal
OAuth2 partner API requiring business registration, not a free personal-
use path — checked directly against `iot.midea.com`'s own docs), not in
any open-source project checked (`midea-beautiful-air`, the
`wuwentao/midea_ac_lan` community guide for the *different*, unrelated
"SmartHome" cloud, or anywhere else searched), and not in any public forum
post found.

**How this project's own copy of them was obtained is explicitly not a
reproducible method for an ordinary owner**: static analysis of the
TSmartLife Android APK was exhausted first (the pre-install `classes.dex`
is provably near-empty — shielded, not just obfuscated), so the values
were ultimately recovered via a heap-dump memory analysis of the live,
rooted-emulator-run app. This required: a disposable rooted Android
emulator, root access, ADB, and a multi-day structured reverse-engineering
process. **An ordinary Vietnamese Toshiba owner cannot be expected to
reproduce this**, and this project does not ask anyone to try.

## What this means practically, today

- **For this project's targeted app variant (TSmartLife "oversea",
  Vietnam)**: nothing to do — the built-in default covers it, see
  "Resolved" above.
- **For a different TSmartLife app variant/market**: you need your own
  copy of that variant's 4 values. The extraction method above explains
  what that actually took for this project's own variant — it is not a
  casual weekend task, and this project does not ask anyone to repeat it.
  Override via `--config-file`/env vars once you have them.
- Whether to publish *this project's* Vietnam-variant values was a
  deliberate decision requiring the maintainer's explicit approval (not
  something a contributor should decide unilaterally) — that approval was
  given for exactly these 4 values, see "Resolved" above. The same
  decision would need to be made again, separately, for any other app
  variant's values before this project would ship them too.

### Trade-offs that were weighed before publishing (for the record)

- **For**: this is the one thing that makes the entire pipeline genuinely
  plug-and-play for a Vietnamese TSmartLife owner on this app variant —
  the actual goal of this project. This is why the maintainer approved it.
- **Against, still true, now accepted as a known risk rather than a
  reason not to publish**: these values are reverse-engineered from a
  vendor's closed app; publishing them is more conspicuous than keeping
  them in a private channel, and the vendor could rotate them in a future
  app update, breaking this default for everyone at once. If/when that
  happens, this document and the shipped default will need updating —
  flagged here so it isn't a silent surprise later.

## Checked this round, for completeness (none of these unblock layer 2)

- **`midea_ac_lan` has graduated into Home Assistant Core** (reported as
  "Midea" integration since HA 2026.8, per Home Assistant's own community/
  docs — not independently re-verified against `home-assistant/core`'s
  source this round, flagged as a lower-confidence claim than the items
  below that were checked against actual source). If accurate, recent HA
  installs may not need HACS/manual installation of `midea_ac_lan` at all.
  This would simplify step 4 below, but does **not** touch layer 2.
- **"Toshiba Lifestyle" is a different, already-solved integration —
  verified against actual source, not just the name.** Checked
  `upstream/main` of `midea-lan` directly: its `SUPPORTED_CLOUDS` table
  has exactly 5 entries — 美的美居 (`MeijuCloud`), `SmartHome`, `Midea Air`,
  `NetHome Plus`, `Ariston Clima` — **no `TSmartLife`, no "Toshiba
  Lifestyle" entry anywhere**. "Toshiba Lifestyle" (reported as an HA-Core
  discovery label with ~1,520 installs) almost certainly covers a
  *different* Toshiba product line (air conditioners, going through one of
  those 5 already-solved clouds) — **not** the TSmartLife-branded
  refrigerator/kitchen-appliance app this project targets. Do not conflate
  the two; a working "Toshiba Lifestyle" setup does not imply TSmartLife
  works.
- **No other TSmartLife fork/tool found** (web search, this round):
  `wuwentao/midea_ac_lan#364` (the original feature request, still open,
  now also referencing a Toshiba washing machine with the same unsolved
  cloud) and our own PR #198 remain the only places TSmartLife support is
  even attempted, anywhere found.

## What would change this

- Midea/Toshiba publishing an official, free, personal-use token-issuance
  path (checked: does not currently exist for personal use — the
  documented partner API requires formal business registration).
- The upstream `midea-lan` maintainer obtaining the same 4 values
  independently and merging them into the published `SUPPORTED_CLOUDS`
  table (the maintainer has asked contributors to find them via APK
  analysis, consistent with this being the project's established, if
  unscalable, method today).
- A future TSmartLife app version exposing the same "Configure manually"
  pattern other Midea-family clouds already support in some newer
  releases — not confirmed to exist for TSmartLife specifically.

None of these are assumed to be imminent. This document will be updated,
not quietly patched over, if the situation changes.
