"""toshiba-tsmartlife-local: onboarding helper for TSmartLife LAN credentials.

See the project README for scope and usage. This package deliberately does
not implement any LAN protocol or Home Assistant entity logic itself -- it
only drives the existing `midealan` cloud client to retrieve a device's
LAN token/key, for use with the separate `midea_ac_lan` HA integration.
"""

__version__ = "0.1.0"
