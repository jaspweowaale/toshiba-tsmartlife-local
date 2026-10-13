# Developer guide: adding another model or market

This project is intentionally thin. Most of what you'd think to "add" for
a new model actually belongs **upstream**, in `midea_ac_lan`'s own 0xCA
entity table — not here.

## If your Toshiba (or other Midea-family) fridge is also device type 0xCA

You likely need **zero code changes anywhere**. `midea_ac_lan` already
supports 0xCA generically. Try:

1. Run `python -m midealan.cli discover` to confirm your appliance is
   discoverable on your LAN (device type should show as `0xca`).
2. If you already have a LAN token/key (e.g. recovered independently, or
   via this project's CLI once you have the layer-2 app constants, see
   `docs/TOKEN_ONBOARDING.md`), configure `midea_ac_lan` directly — this
   project isn't involved at that point.
3. If your app isn't TSmartLife but another Midea-family rebrand, check
   whether `midealan.cloud.SUPPORTED_CLOUDS` already lists it. If so, this
   project's onboarding CLI already works for it too (just change which
   cloud name you pass) — though it isn't tested against any cloud other
   than TSmartLife.

## If your model needs genuinely different protocol decoding (not 0xCA)

That belongs in `midea-lan`/`midea_ac_lan` upstream, not here — this
project has no protocol-decoding code of its own to extend. Open an issue
or PR against those projects instead.

## If your market's TSmartLife app uses different layer-2 app constants

This is plausible but **unverified** — different market variants of an
app sometimes share build-time constants and sometimes don't. If you
independently obtain your own market's 4 values and confirm the CLI works
end-to-end, please report back (sanitized — do not paste the actual
values in an issue) so this document can note which markets are confirmed
to share constants vs. not.

## Running the tests

```bash
pip install -e ".[dev]"
pytest tests/
```

All tests are offline and mock the cloud client entirely — no network
access, no real credentials, ever required to run them.

## Code style

This project has no `ruff.toml`/lint config of its own yet — if you add
one, match `midea-lan`'s own `ruff.toml` conventions for consistency,
since contributors will likely move between both repos.
