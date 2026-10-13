# Known limitations

All findings below come from direct testing against one physical unit
(see README for the exact model) over several days, not assumption.

## Humidity does not work — root cause known, not a mystery

The `humidity` entity exposed by `midea_ac_lan` for this device type reads
a 3-bit raw protocol field (`body[27] & 0x70`), but the integration only
maps **two** of its eight possible raw values to a string (`0x10`→"high",
`0x20`→"low"); every other raw value — almost certainly including this
unit's normal/idle value — returns nothing, which Home Assistant shows as
`unknown`. This was confirmed consistent across two independent reads
taken a day apart. **This is architecturally a discrete humidity-control-
mode flag, not a continuous %RH sensor.** Do not display it as if it
measures relative humidity.

## Only two door groups, not four individually-addressable doors

This refrigerator has four physical doors, but across the integration's
entire operating history on the tested unit, only two of the four
protocol-level door entities have ever reported a state change: the one
mapped to the upper compartment and the one mapped to the lower
compartment. The other two (a third/fourth door-style entity and a
"bar door" entity) have never fired once. Whether this reflects wiring
this specific model doesn't use, or simply doors that happen never to have
been tested individually, was not conclusively settled — a live, one-
door-at-a-time physical test was the only way to settle it, and that
investigation is outside this project's scope. **Only claim "upper" and
"lower" door-group state as working; do not claim individual left/right
detection.**

## No instantaneous power/wattage from the Toshiba LAN protocol

No entity anywhere in this device type's table exposes live power draw in
watts. A cumulative `energy_consumption` (kWh) field exists in the
protocol, but on the tested unit it read a flat `0` for its entire
observed existence and should not be trusted. **If you want real power/
energy monitoring, pair an independent smart plug** (any standard
energy-monitoring smart plug Home Assistant already supports) — this is
a deliberate recommendation, not a workaround for a project failure.

## No 48h+ operating history exists yet for any of the above

These findings come from a single testing window. They are the best
information available, not a guarantee that behavior is identical on every
unit of this model, let alone other Toshiba models.
