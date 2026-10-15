# Cloud Independence Research — LAN V3 Authentication & Offline Provisioning

**Status: research findings, not a working offline-provisioning solution.** This
document traces the *already-working* LAN V3 authentication mechanism with
exact source citations, and documents what evidence exists (and doesn't) for
provisioning credentials without the TSmartLife cloud. It deliberately does
not include any proprietary APK source, extracted binaries, or real device
credentials — citations point to file/line locations in the already-open-source
`midea-lan` library and to this project's own prior research logs.

## 1. What's already solved

This device (Toshiba GR-RF900WI-PMV(06)-MG) has been running entirely on LAN,
with **zero ongoing cloud dependency**, since the credentials were first
obtained. The cloud is only needed to *mint* the credential once — not for any
subsequent connection. This is proven, not assumed: a live LAN read, performed
independently of any cloud call, reused only the already-saved token/key file
and succeeded on the first attempt (31 real telemetry fields read back
correctly).

## 2. The LAN V3 handshake, with exact code citations

All citations below are to `midealan/` in the open-source
[`midea-lan`](https://github.com/wuwentao/midea-lan) library (the same code
this integration and the upstream `midea_ac_lan` Home Assistant integration
both run).

**Discovery** (`midealan/discover.py:281`, `discover()`): a UDP broadcast scan
across the local network's broadcast addresses, parsed by
`_parse_discover_response()` (`discover.py:192`). Device type `0xCA` (this
fridge's type byte) is a recognized value in the discovery response parser
(`discover.py:137`). Nothing here involves the cloud — pure LAN broadcast/reply.

**Handshake** (`midealan/device.py:333`, `authenticate()` — V3 only):
1. The already-obtained `token` (32 bytes, hex-decoded from the saved
   credential file) is sent to the device, framed via `encode_8370()`
   (`security.py:376`) with message type `MSGTYPE_HANDSHAKE_REQUEST`. This
   message type is *not* one of the two types `encode_8370` AES-encrypts
   (`security.py:383`), so the token itself travels over the wire in the clear
   at this step — its secrecy isn't what's protecting the exchange; what
   happens next is.
2. The device replies; bytes `[8:72]` of that reply are passed to
   `LocalSecurity.tcp_key(response, key)` (`security.py:360`).
3. `tcp_key()`: AES-CBC-decrypts the first 32 bytes of the response using the
   already-obtained `key` (not the token), computes `SHA256` of the decrypted
   plaintext, and requires it to exactly match the trailing 32 bytes of the
   response (the device's own signature). If it doesn't match,
   `DataSignDoesntMatch` is raised and authentication fails.
4. On success, the actual session key is derived as
   `strxor(decrypted_plaintext, key)` — a local, per-connection XOR, not
   persisted across reconnects (`self._request_count`/`_response_count` are
   reset to 0 at the same point).

**Ongoing traffic**: once authenticated, `encode_8370()`/`decode_8370()`
AES-CBC-encrypt all real command/status traffic using the derived session key,
with a running counter and a `SHA256`-based integrity check per message
(`security.py:376-410`).

## 3. What's a manufacturer constant vs. a real secret

`LocalSecurity.__init__` (`security.py:315-329`) hardcodes two fixed values
library-wide: `self.aes_key` and `self.salt` — these are manufacturer-wide
constants baked into the open-source library itself, not secrets, and are used
by *other* helper methods (`aes_encrypt`/`aes_decrypt`/`encode32_data`), not by
the V3 handshake's own `tcp_key()` step.

**The actual authentication-critical secret is `self._key`** — passed into
`tcp_key()` as a parameter, never read from any fixed/hardcoded constant in
this codebase. It's supplied entirely externally, from the already-obtained
per-device credential file. This is the single fact that answers most of the
open questions below: **the device's own copy of this key is not something the
LAN protocol itself ever reveals, derives, or lets you set** — it's simply
assumed to already match on both sides, established once, elsewhere.

## 4. Which values are what

| Value | Origin | Persists? | Evidence |
|---|---|---|---|
| `token` | Cloud-issued (`get_cloud_keys()`) | Yes, reused every connection | `lan_credentials.json`, confirmed working via live reconnect test |
| `key` | Cloud-issued, paired to the token | Yes, reused every connection | Same source; used directly in `tcp_key()`, never regenerated locally |
| Session key (`_tcp_key`) | Derived locally, per-connection | No — fresh XOR derivation every connect | `security.py:360-373` |
| `aes_key`/`salt` | Fixed manufacturer constants, library-wide | N/A (not a secret) | `security.py:315-326` |

## 5. Offline credential generation — evidence-based assessment

Using the categories this investigation set out to test:

- **(A) Recovering a stored device secret** — **this is what's already been
  done**, and it's the only approach with direct, verified evidence of working.
  The token/key pair already existed (minted once, during this device's
  original cloud pairing) and was recovered via one authenticated cloud call,
  then backed up locally. No further cloud contact is needed to keep using it.
- **(B) Deriving credentials from known material** — **no supporting evidence
  found**, despite extensive prior investigation (this project's own earlier
  stages did real static/native decompilation of the TSmartLife app across
  multiple libraries, specifically hunting for the token-issuance logic). The
  actual token-generation endpoint's internal logic was **never found
  client-side, anywhere** — strong evidence it's computed server-side only,
  not something the app (and therefore not something external analysis of the
  app) can reveal. No brute-forcing was attempted or is recommended — nothing
  found suggests the key space is small or predictable.
- **(C) Provisioning a new owner-controlled key** / **(D) Reproducing an
  authorized pairing process** — **genuinely unresolved, the real remaining
  gap**. The open-source LAN protocol itself has no "set new key" or
  "re-provision" operation — `tcp_key()` only ever *verifies* an existing
  shared secret, it never establishes one. Whatever process originally wrote
  this device's key into its own flash storage (presumably during its
  cloud-mediated first-time pairing) hasn't been identified or reproduced
  locally.
- **(E) Replacing a necessary cloud service** — follows directly from (C)/(D)
  being unresolved: if there's no local way to (re-)provision a key, a
  cloud-free *future* pairing would require either finding a local
  provisioning path that already exists on-device (unconfirmed) or standing up
  a replacement for whatever the cloud currently does during pairing (not
  attempted, no evidence yet that this is even architecturally possible).

**Bottom line**: cloud independence for *continued use of an already-paired
device* is solved and proven. Cloud independence for *initial pairing or
re-pairing* is not — and nothing found in this investigation suggests it's an
easy local derivation; the evidence points toward (D)/(E), not (B).

## 6. Lua/plugin status

**Update 2026-10-15**: upstream cloud-support PR
https://github.com/wuwentao/midea-lan/pull/198 has **merged** into
`wuwentao/midea-lan:main` (merge commit `6748eb6266eb756e038faf5d9024428aa94820ab`,
merged by the maintainer). TSmartLife cloud support is now part of upstream
main itself, independently confirmed via the GitHub API and a direct content
check of `midealan/cloud.py` on `main`.

The Lua/plugin test-coverage branch has been rebased directly onto real
upstream `main` and opened as a proper cross-repo PR:
**https://github.com/wuwentao/midea-lan/pull/215** (open, **draft** —
deliberately not marked ready for review yet). The earlier fork-only stacked
PR (https://github.com/jaspweowaale/midea-lan/pull/1), which existed only
because #198 hadn't merged yet, has been closed with a comment pointing to
#215.

- `TSmartLifeCloud.download_lua`/`download_plugin` correctly inherit
  `SmartHomeCloud`'s implementation (verified structurally and via mocked
  end-to-end tests — **still not yet exercised against the real cloud** with
  this device's real serial number; that live test remains a separate,
  explicitly-gated step, not yet executed).
- Full suite: 2865/2865 passing against current upstream `main`, ruff clean,
  no new mypy issues.
- PR #215 is intentionally left in draft state until the live validation
  actually happens — it will be updated with real results and marked ready
  for review at that point, not before.

## 7. App functions with protocol support but not yet in Home Assistant

- **Defrost/deicing status**: the 0xCA protocol decodes
  `freezing_motor_deicing_status` plus several defrost-error/overtime bits
  (`midealan/devices/ca/message.py:134-215`), but the installed `midea_ac_lan`
  version doesn't expose any of them as HA entities yet. A real temperature
  spike pattern consistent with a defrost cycle was observed in HA history but
  couldn't be confirmed against this bit, precisely because it isn't exposed.
- **Firmware update**: partially already surfaced — `update.new_refrigerator`
  and `update.temperature_refrigerator` entities exist in the live HA
  instance, so this isn't a full gap, just worth noting as already covered
  rather than missing.
- **Network/WiFi status**: no evidence found of a LAN-protocol-level field for
  this on the 0xCA device; if it exists at all, it's more likely only visible
  via the cloud's appliance-listing metadata (not investigated this round) —
  flagged as an open question, not a confirmed gap.

## 8. Next experiment proposal

**Hypothesis**: the device's own first-time pairing flow (AP-mode/BLE setup,
triggered when unpaired) may involve the phone app talking **directly** to the
device for at least part of the credential exchange, with the cloud used
primarily for account/ownership bookkeeping rather than being the sole origin
of the LAN key material. If true, there could be a local-only provisioning
path that's never been observed because this project has never captured or
analyzed an actual pairing event at the protocol level.

**Test method**: passive network capture (not interception, not decryption of
TLS) during a real, owner-initiated re-pairing of a device — observing
whether any pre-cloud-login local traffic (AP-mode HTTP, BLE GATT, or LAN
broadcast) carries key-shaped material before the app's cloud login completes.

**Required access**: a real pairing event. This is the hard constraint —
either a spare/second Midea-protocol device (zero risk to the production
fridge) or a deliberate, explicitly-authorized reset-and-re-pair of the real
fridge (destructive, currently out of scope per standing instruction).

**Expected evidence**: either (a) key-shaped material appears in local traffic
before any cloud call completes — supporting a local provisioning path worth
pursuing further — or (b) no local traffic carries anything key-shaped before
the cloud login — which would directly confirm category (E) as the real
situation and close this line of investigation with evidence rather than
assumption.

**Risks**: none to data in flight (passive capture only); the real risk is
entirely in the *pairing event itself* if done on the production fridge
(temporary loss of LAN control until re-paired, possible need to
re-authenticate HA's integration). Recovery: the already-verified backup
credential plus this project's existing re-pairing documentation.

**Physical refrigerator access needed**: yes, if tested on the real device —
this experiment cannot be run without an actual pairing event happening
somewhere. Recommended: wait for a spare device, or get your explicit
go-ahead for a scoped, supervised re-pair test on the real one.
