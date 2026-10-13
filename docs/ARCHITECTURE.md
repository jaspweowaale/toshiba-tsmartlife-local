# Architecture decision

## The 6 candidate architectures, compared

| # | Architecture | Can authenticate to the fridge? | Reads LAN temp/door data? | Needs another integration? | Needs ongoing cloud access? | HACS-installable? | UI config? | Easy to add other Toshiba models? | Maintenance | Reuse of existing working code |
|---|---|---|---|---|---|---|---|---|---|---|
| 1. HA blueprint only | No | No | **Yes, always** — see note below | No | N/A (not an integration) | N/A | N/A | N/A | Trivial | None — can't create entities |
| 2. New HA custom integration using `midealan` | Yes (same protocol) | Yes | No | No (once set up) | Yes | Yes, if published | Yes (config flow) | Same effort as upstream already spent | High — a second codebase to track upstream changes forever | Duplicates `midea_ac_lan`'s already-working 0xCA table for no reason |
| 3. New Toshiba-specific HACS integration from scratch | Yes | Yes | No | No | Yes | Yes | Yes | Only as easy as we make it | Highest — full integration lifecycle, HA API churn, HACS listing upkeep | Would reinvent `midea_ac_lan` |
| **4. Standalone Python onboarding helper + reuse `midea_ac_lan` (RECOMMENDED)** | Yes | Yes (via `midea_ac_lan`, already proven) | **Yes — `midea_ac_lan` itself** (by design) | No, if already has `midea_ac_lan` | No, after one-time onboarding | Helper: no (plain pip CLI); integration: yes, already is | Yes, via `midea_ac_lan`'s existing config flow | Just document the new model + confirm the CLI onboarding works | Low — small, single-purpose tool | Maximizes reuse of both `midealan` (library) and `midea_ac_lan` (integration) |
| 5. Fork `midea_ac_lan` | Yes | Yes | No | No | Yes | Yes | Yes | High — diverges from upstream immediately, loses future upstream fixes/features | 0xCA is already upstream; forking buys nothing |
| 6. Fully independent LAN protocol implementation | Yes, eventually | Yes, eventually | No | No | Yes | Yes | Yes, but from zero | Highest — reimplementing and maintaining an entire protocol stack | None — the protocol decoder is already proven correct against the real device |

**Note on blueprints (the task's own caution, confirmed true)**: a
Lovelace/automation blueprint can only reference entities that *already
exist*. It cannot open a socket, authenticate, or create a sensor entity.
Every one of options 1 is therefore unusable as the primary solution — a
blueprint can, at most, be an *optional* add-on once entities already
exist from something else (see `examples/blueprints/`).

## Recommendation: Option 4

**Build a small, standalone Python onboarding CLI. Do not build a new HA
integration, and do not fork `midea_ac_lan`.**

Reasoning, in order of weight:

1. **The LAN/entity side is already solved, upstream, for this exact
   device type.** `midea_ac_lan` already ships a complete entity table for
   device type `0xCA` and was confirmed working against this exact
   physical refrigerator with zero custom code (see the project's own
   Stage 4N/4O history: 21 live entities, values cross-checked against an
   independent sensor). Rebuilding this (options 2, 3, 5, 6) would violate
   the project's own stated principle: *"Do not reinvent working protocol
   code unless there is a meaningful technical reason."* There isn't one.
2. **The actual gap is narrow and well-defined**: getting a *TSmartLife*-
   paired appliance's LAN `token`/`key` into a form `midea_ac_lan`'s
   existing "Configure manually" config-flow step can consume. That's a
   few dozen lines of CLI wrapper around an already-published, MIT-
   licensed library (`midea-lan`) — not a reason to build or maintain an
   entire second integration.
3. **Lower burden on users.** Someone who already has `midea_ac_lan`
   installed for another Midea-family appliance doesn't need to install
   *anything* in Home Assistant for this project — they run one CLI
   command once, on their own computer, and paste two values into a config
   flow they already know.
4. **Lower burden on us.** A thin CLI has no HA API to track across
   releases, no HACS listing to maintain, no entity-platform churn to
   follow. The actual protocol work stays the sole responsibility of
   `midea-lan`/`midea_ac_lan`'s own maintainer and community — exactly
   where ongoing protocol maintenance belongs.
5. **Honest about what's actually unsolved.** The real unsolved problem
   (see `docs/TOKEN_ONBOARDING.md`) is credential *reproducibility* for
   other users, not protocol engineering. A new integration would not
   make that problem any more solvable — only a clear, separate onboarding
   tool addresses it directly.

This does not preclude *also* contributing improvements upstream (see the
project's Stage 4 upstream-contribution work, kept on its own branch) —
the two tracks are complementary, not competing.
