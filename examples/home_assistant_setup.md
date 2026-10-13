# Example Home Assistant setup

`midea_ac_lan` is configured through its own UI config flow, not YAML —
there is no `configuration.yaml` snippet to copy for the integration
itself. The steps:

1. Install `midea_ac_lan` via HACS (or manually) if you don't already have
   it — see that project's own README.
2. Settings → Devices & Services → Add Integration → "Midea AC LAN".
3. Choose **"Configure manually"** (not cloud login) when adding your
   Toshiba appliance.
4. Device type: `0xCA`. Protocol: `V3`. Enter the IP address (find it via
   `python -m midealan.cli discover`, or your router's client list) and
   the `token`/`key` this project's onboarding CLI printed for you.
5. After adding the device, go to the integration's **Options** (not the
   initial setup) and explicitly select which entities to enable — for
   device type 0xCA, none are enabled by default until you pick them here.
   Based on this project's own testing, enable at least:
   - `refrigerator_actual_temp`, `refrigerator_setting_temp`
   - `freezer_actual_temp`, `freezer_setting_temp`
   - `flex_zone_actual_temp`, `flex_zone_setting_temp`
   - `refrigerator_door` (upper), `freezer_door` (lower)

   See `docs/KNOWN_LIMITATIONS.md` before enabling anything else (several
   other entities in the generic table are confirmed not meaningful for
   this tested unit).

The resulting entity IDs will be prefixed with your device's own numeric
ID, e.g. `sensor.<your_device_id>_refrigerator_actual_temp` — substitute
your own value anywhere the dashboard example below shows
`YOUR_DEVICE_ID`.
