"""Built-in default TSmartLife app-level configuration ("Vietnam" preset).

These 4 values are the shared, app-wide constants every copy of the
TSmartLife "oversea" Android app ships with (see
``docs/APP_CREDENTIAL_SECURITY.md`` for the full classification). They are
**not** per-account or per-device secrets: they do not, by themselves,
grant access to any specific person's account or appliance -- a separate
username/password (always entered interactively by the user, never
stored here) is required for that.

Publishing these here is a deliberate, explicit, one-time exception made
by this project's maintainer after reviewing
``docs/APP_CREDENTIAL_SECURITY.md`` -- not a change to this project's
general policy on secrets. Nothing else in this project embeds a
credential of any kind. If you fork this file for a different
region/app variant, add a new named preset rather than overwriting this
one; see ``docs/USER_GUIDE.md``.

This default is used only when no explicit override is supplied (see
``onboard.py:_read_app_constants`` for the exact precedence order) --
anyone who wants to use a different app variant's constants can still do
so via ``--config-file``/``$TSMARTLIFE_CONFIG_FILE``/the 4 individual
environment variables, all of which take full priority over this file.
"""

from __future__ import annotations

VIETNAM_DEFAULT: dict[str, str] = {
    "app_id": "1020",
    "app_key": "d1ba2a7513bef7bbcd58478b678ff655",
    "iot_key": "meicloud",
    "hmac_key": "PROD_VnoClJI9aikS8dyy",
}
