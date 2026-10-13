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
   the app's. This is the one layer this project has not solved
   reproducibly for anyone else (see below).
3. **Appliance-specific LAN token/key** — unique per physical appliance,
   derived automatically from (1) + (2) via the cloud's `getToken` API.
   Fully automated by this project's CLI once (2) is available.
4. **Local LAN protocol handshake + ongoing local operation** — already
   solved, upstream, by `midea_ac_lan`. Once (3) is configured there, no
   further cloud contact of any kind is required for ongoing use
   (confirmed by direct testing: a fresh `login()` is needed only to
   obtain (3), never again afterward).

## What's reproducible right now, for anyone

Once layer 2's 4 values are available to you (see below), **the entire
rest of the process is a single CLI command with your own account**:

```bash
export TSMARTLIFE_APP_ID=...      # layer 2 -- see "The real blocker" below
export TSMARTLIFE_APP_KEY=...
export TSMARTLIFE_IOT_KEY=...
export TSMARTLIFE_HMAC_KEY=...

toshiba-tsmartlife-onboard --username you@example.com --device-sn <your SN>
```

This performs layers 1 and 3 automatically — no APK work, no Android
emulator, no reverse engineering, by design. It was built specifically so
an ordinary owner never has to repeat what this project's own development
required (see below).

## The real blocker: layer 2 has no known reproducible, documented path

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

- If you already have a copy of the 4 values (e.g. shared directly by
  this project's maintainer, or recovered independently), the CLI above
  works for you right now.
- If you don't, **there is currently no user-friendly, documented way for
  you to get them yourself**. This is stated plainly rather than papered
  over with a fake workaround.
- The decision of whether to publish this project's own already-recovered
  copy of the 4 values (inside this repo, in a release artifact, or kept
  private and shared individually) is a deliberate policy choice with real
  trade-offs (see below) — it is **not** made by this document, and is
  flagged in the project handoff as requiring the maintainer's explicit
  approval, not something a contributor should decide unilaterally.

### Trade-offs to weigh before publishing layer-2 values

- **For**: this is the one thing that would make the entire pipeline
  genuinely plug-and-play for any Vietnamese TSmartLife owner — the actual
  goal of this project.
- **Against**: these values are reverse-engineered from a vendor's closed
  app; publishing them is more conspicuous than keeping them in a private
  channel, and the vendor could rotate them in a future app update,
  breaking this project's onboarding path for everyone at once (whereas a
  quieter distribution channel might persist longer, at the cost of being
  less "ordinary-user-friendly").
- This project takes no position on which trade-off is correct — that is
  the maintainer's call.

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
