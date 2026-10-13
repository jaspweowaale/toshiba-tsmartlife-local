# Attribution notice

This project (`toshiba-tsmartlife-local`) is an independent, separately
maintained open-source project. It is not affiliated with Toshiba, Midea,
or the maintainers of the projects below, and provides no warranty.

## Dependencies reused as-is (not forked, not copied)

- **[`midea-lan`](https://github.com/wuwentao/midea-lan)** (MIT, © 2026
  Wentao Wu, © 2021 George Zhao) — the LAN/cloud protocol client library
  this project's onboarding helper imports and calls. No source from this
  project has been copied into this repository; it is a normal package
  dependency. See that project's own `LICENSE` file for its exact terms.

## Recommended companion project (separate install, not a dependency of this repo)

- **[`midea_ac_lan`](https://github.com/wuwentao/midea_ac_lan)** — the
  Home Assistant custom integration that actually creates the sensor/
  binary_sensor entities once you have a LAN token/key. This project does
  not install, configure, or modify it — it only documents how to use the
  token/key this project's helper produces with it.

## Origin of the TSmartLife cloud support referenced by this project

The ability to authenticate against the TSmartLife cloud and recover a
device-specific LAN token/key was originally developed as a draft
contribution to `midea-lan`:
[PR #198](https://github.com/wuwentao/midea-lan/pull/198) (work in
progress, not yet merged, draft status as of this writing). That work, and
this project, were both produced with the assistance of Claude Code
(Anthropic), directed by the appliance's owner.

**Because of that unmerged status**, this project's `pyproject.toml`
currently depends on our own fork's branch
(`jaspweowaale/midea-lan@feat/tsmartlife-cloud-draft`, the exact branch PR
#198 is built from) rather than plain `wuwentao/midea-lan@main` — upstream
`main` does not yet define TSmartLife cloud support at all, so depending
on it directly would make this entire tool non-functional. This is a
temporary, clearly-marked pin (see the comment in `pyproject.toml`); it
will switch back to the plain upstream URL once PR #198 merges.

## No private data in this repository

No real application keys, device LAN tokens/keys, account passwords,
session tokens, serial numbers, or other identifying appliance details
belonging to any real device are present anywhere in this repository's
history. Any credential-shaped string in documentation or examples is a
placeholder and will not authenticate against anything.
