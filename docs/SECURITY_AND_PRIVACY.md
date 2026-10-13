# Security and privacy notes

- **Your TSmartLife password** is read via a hidden terminal prompt
  (`getpass`) and held in memory only for the duration of one login call.
  It is never written to disk, logged, or transmitted anywhere other than
  the TSmartLife cloud's own login endpoint (the same endpoint the
  official app itself uses).
- **The resulting LAN token/key are specific to your appliance.** This
  tool prints them once, to your own terminal, for you to paste into Home
  Assistant yourself. It does not store them, send them anywhere else, or
  log them to a file.
- **The 4 shared app-level constants** (see `docs/TOKEN_ONBOARDING.md`)
  are read from environment variables you set yourself. This project's
  own source code and git history contain no real values for these —
  only placeholder strings in documentation and tests, which will not
  authenticate against anything.
- **Logging in to the TSmartLife cloud with your account from a second
  place (this tool) may interrupt the official mobile app's own active
  session** — this was observed directly during this project's own
  development (the Midea cloud backend appears to enforce one active
  session per account at the token level). It is not destructive and the
  mobile app can simply be reopened/re-logged-in afterward, but don't be
  alarmed if it happens.
- **After onboarding, no further cloud contact is required or performed**
  by `midea_ac_lan` for ongoing local operation — confirmed directly: the
  LAN token/key, once obtained, authenticate entirely over your local
  network. The appliance itself may still independently contact Midea's
  cloud on its own (for the vendor app's own remote-access features) —
  that is appliance firmware behavior, outside this project's or
  `midea_ac_lan`'s control, and happens whether or not you ever run this
  tool.
- **Do not commit** your own `TSMARTLIFE_*` environment variables, your
  account password, or your appliance's token/key/serial number to any
  git repository, issue, or chat log. The `.gitignore` in this repo
  excludes common accidental-leak patterns, but ultimately this is a
  human-discipline requirement, not something software can fully enforce.
