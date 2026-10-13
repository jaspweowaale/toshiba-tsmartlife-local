# Security and redistribution analysis: the 4 TSmartLife app-level constants

This document classifies `app_id`, `app_key`, `iot_key`, and `hmac_key`
(referred to throughout this project as "layer 2" — see
`TOKEN_ONBOARDING.md`). **No actual value of any of these 4 constants is
printed anywhere in this document, this repository, or its git history.**
Everything below is based on their *role in the protocol* and on
*publicly verifiable facts about upstream's own repository* — not on
anything that would require disclosing our own recovered copies.

Findings are explicitly separated into three confidence tiers:
**CONFIRMED** (directly observed, verifiable by anyone against public
sources), **INFERENCE** (reasoned from confirmed facts, not independently
proven), and **UNKNOWN** (genuinely not established — stated as such, not
guessed).

## 1–3. Role, identifier-vs-secret, signing-vs-access (combined)

| Constant | Role | Identifier or secret? | Function |
|---|---|---|---|
| `app_id` | Identifies *which app* is calling the cloud (e.g. sent as the `x-recipe-app` header) | **Identifier** — CONFIRMED. Comparable to an OAuth `client_id`. Travels in plaintext in every single API request this app makes, visible to anyone who inspects their own device's network traffic. | Routing/attribution, not access control |
| `app_key` | Paired with `app_id` in an HTTP Basic-Auth-shaped header for a subset of endpoints | **Shared-secret-shaped, but see §5** | Authenticates "this is a genuine copy of the app," not any specific user |
| `iot_key`, `hmac_key` | The two inputs to the app's request-signing function (HMAC-SHA256-family) | **Shared-secret-shaped, but see §5** | Lets the cloud verify a request wasn't tampered with in transit / wasn't forged by an arbitrary unsigned client |

**CONFIRMED, critical point**: none of these 4 constants, alone or
together, authenticate as a *specific user* or grant access to any
*specific appliance*. A separate, per-account username/password (never
proposed for distribution anywhere in this project) is required for that.
Possessing all 4 constants lets a party construct syntactically valid,
correctly-signed requests *to Midea's gateway* — it does not let them log
in to anyone's account or read anyone's appliance data without also
having that account's own password.

## 4. Shared across all users, or per-user?

**CONFIRMED — shared, not per-user.** This is explicitly how the
upstream `midea-lan` library's own `SUPPORTED_CLOUDS` table is
structured: one fixed set of 4 values per *cloud/app* (5 entries exist
today: 美的美居, SmartHome, Midea Air, NetHome Plus, Ariston Clima — each
with its own single, shared `app_id`/`app_key`/`iot_key`/`hmac_key`,
verified directly against `upstream/main`'s `midealan/cloud.py`), not one
set per installation or per user. Every person who has ever installed a
given app has the exact same 4 values sitting in their copy.

## 5. Disclosure risk if published

**INFERENCE, reasoned from confirmed facts:**

- **These values are already present, in recoverable form, inside every
  copy of the TSmartLife app installed on every user's phone.** They are
  not server-side secrets; they are client-side constants shipped to an
  uncontrolled, mass-distributed population of devices. This is the
  well-understood "client-side secret" limitation: a string embedded in
  software handed to the public is protected only by the *effort* required
  to extract it, not by cryptography — and this project's own development
  history is direct proof that extraction is achievable (it took a
  multi-day structured effort, not a trivial one, but it was done without
  any insider access).
- **Marginal risk of publication is therefore the *difference* between
  "requires APK reverse-engineering skill" and "requires reading a GitHub
  repo"** — a real reduction in effort for a motivated bad actor, but not
  the creation of a capability that didn't already exist. This is a
  genuine, non-zero increase in risk, not a non-issue.
- **What publication would NOT do**: grant access to any specific
  person's account or appliance (see §1–3), or materially help an
  attacker who already has the skill to extract app internals (which this
  project's own method proves is a solved problem for a sufficiently
  motivated party regardless of what we publish).
- **What publication plausibly WOULD do**: make it marginally easier for
  third parties to build unauthorized TSmartLife-compatible clients at
  scale (e.g. scraping, abuse automation) by removing the one-time
  extraction step. This is the most honest characterization of the real
  risk — a *scale/convenience* risk for bad actors, not an *access*
  risk for individual users' data.

## 6. Revocation / service-disruption risk if Midea/Toshiba notices

**INFERENCE:** If Midea rotates these 4 values in a future app update
(something they control unilaterally and could do for unrelated reasons,
not necessarily in response to this project), every user relying on them
— including this project's own maintainer — loses the ability to obtain
new LAN tokens via this method simultaneously, with no advance warning.
This was already flagged in `TOKEN_ONBOARDING.md` as a trade-off. It is a
**service continuity risk to users of this project**, not a security risk
to Midea's infrastructure or other users' accounts.

## 7. Known upstream precedent — CONFIRMED, checked against actual source

**Upstream `midea-lan`'s own public, MIT-licensed repository already
publishes all 4 equivalent constant types, in plaintext, for 5 different
clouds — not merely "could," but **does, today, continuously, as normal
supported functionality**.** Verified directly against
`git show upstream/main:midealan/cloud.py` (not assumed, not taken from a
README): the `SUPPORTED_CLOUDS` dictionary contains literal `app_id`,
`app_key`, `iot_key`, and `hmac_key` values for 美的美居 (`MeijuCloud`),
`SmartHome`, `Midea Air`, `NetHome Plus`, and `Ariston Clima`. Notably,
the `hmac_key` literal for 美的美居 and `SmartHome` is **the exact same
value** in both entries — direct confirmation that this specific constant
is shared at the SDK level across sibling Midea-ecosystem apps, not a
uniquely-scoped secret per brand.

This is the single strongest piece of evidence in this whole analysis:
the project this repository depends on, maintained by a different,
established maintainer, already treats these constant types as
publishable, and has done so without any visible dispute, legal action,
or revocation event as of this writing (checked: no issue, PR, or
maintainer comment anywhere in this project's extensive prior research
indicating Midea has objected to any of the 5 already-published clouds).

## 8. Is redistribution permitted, or unclear?

**UNKNOWN — explicitly not resolved, stated honestly rather than
assumed either way.** This project has reviewed Midea's official
`iot.midea.com` developer documentation (covering a *separate*, formal
OAuth2 partner API requiring business registration — not the consumer app
path these 4 constants belong to) and the TSmartLife app's own in-app
screens (Device Information, Mode, Self Diagnostics, Network Info — no
licensing text encountered there). **No EULA, Terms of Service, or
developer agreement specific to the TSmartLife consumer app has been
located or read by this project.** It is common, but not universal, for
mobile app EULAs to prohibit reverse-engineering and redistribution of
extracted internals — absent having actually read Midea's or Toshiba's
specific terms, this project takes no position on whether redistribution
is contractually permitted. §7's precedent shows the *practical* upstream
norm; it does not establish the *legal* position, which remains
unverified.

## 9. Does a realistic alternative onboarding method exist?

**CONFIRMED, already documented in `TOKEN_ONBOARDING.md`**: no. Checked
this project's own research history plus a fresh web search this round:
no official free personal-use token-issuance path, no existing
open-source TSmartLife credential tool, and no other fork or project
anywhere found has solved this. The only two paths that exist today are
(a) APK reverse-engineering (what this project did once, explicitly
flagged as not reproducible by an ordinary owner) or (b) obtaining a copy
of these 4 values from someone who already has them.

## Responsible recommendation for ordinary Vietnamese owners

1. **This document does not change what the repository currently
   contains.** No real value of any of the 4 constants is in this
   repository, in any file, or in git history — confirmed by a dedicated
   scan before every commit this project has made (see
   `PUBLICATION_READINESS.md` for this round's specific scan).
2. **Whether to actually publish, or privately distribute, this
   project's own recovered copy remains the maintainer's decision alone**
   — this analysis does not make that call for them. What it adds, beyond
   `TOKEN_ONBOARDING.md`'s earlier framing, is: strong precedent that the
   *practical* risk is lower than "secret leak" framing would suggest
   (§5, §7), while the *legal/ToS* angle remains a genuine, unresolved
   unknown (§8) that a purely technical analysis cannot close.
3. **If the maintainer does decide to distribute these values**, the
   lowest-risk approach given everything above would be: not committing
   them to the public git history of this repository (where they become
   permanently, trivially scrapeable and attributable to this specific
   project), and instead sharing them through a narrower, revocable
   channel (direct message, a separate non-indexed document, etc.) to
   people who ask — preserving most of the practical benefit while
   keeping the legal/ToS exposure (§8) and the "who published this"
   attribution lower than a public commit would.
4. **For an ordinary owner reading this today**: the honest status is
   still "blocked unless someone gives you these 4 values directly" —
   this document is an analysis of a policy question, not a new
   onboarding path.
