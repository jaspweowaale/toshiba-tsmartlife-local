# Preserve local LAN access: a quick firmware protection guide

**We own our devices. We decide when they update.**

If your Midea or Toshiba appliance already works over the local network, you may be able to preserve that functionality by blocking the appliance's internet access while keeping its LAN connection available. This is a preventive measure, not a way to restore LAN support after firmware has removed it.

The [Midea LAN maintainer has reported](https://github.com/wuwentao/midea-lan/pull/198#issuecomment-7095157868) cases in China where newer firmware removed LAN control. Specific affected models and firmware versions have not been independently verified by this project.

The same maintainer has separately [reported](https://github.com/wuwentao/midea-lan/pull/198#issuecomment-7122333488) that some Midea-based smart-home ("MeiJu"/cloud) appliances contain a hardware/firmware watchdog: if the device cannot reach the manufacturer's cloud within a few minutes, its Wi-Fi/communication module repeatedly disconnects and reconnects while trying to restore cloud contact, citing a [specific reported case](https://github.com/wuwentao/midea_ac_lan/issues/1146#issuecomment-6588470606). A recurring disconnect/reconnect pattern like this is a possible watchdog signature, not proof by itself that the appliance is actually rebooting — but on an affected device it can mean full internet isolation produces unstable, cycling behaviour instead of calm local-only operation. This varies by device branch, app and region — it does not mean every Midea or Toshiba product behaves this way, and our own tested refrigerator (below) shows no such pattern. Verify your own device continues operating normally after isolating it; do not assume our result applies to yours.

## Quick setup

1. **Confirm local operation first.** Complete any required initial onboarding and verify that Home Assistant or your local controller communicates directly with the appliance. Securely retain any LAN token/key and configuration needed for reconnection. Do not post these credentials publicly.
2. **Identify the appliance in your router.** Find its MAC address and current IP in the connected-client list. Use a device-based rule if supported, or reserve its current IP through DHCP so an IP-based rule continues to match it.
3. **Block internet access for this device only.** In your router's firewall, traffic rules or access-control settings, deny all appliance-to-WAN traffic (all destinations, ports and protocols), including IPv6 where available. Ensure unsolicited inbound WAN traffic and existing cloud sessions cannot reach the appliance. Check rule precedence and any alternative internet routes or local proxies. Keep the appliance connected to Wi-Fi/Ethernet and allow the required local traffic to/from Home Assistant. Do not use a whole-network block or a Wi-Fi pause that also cuts off the LAN.
4. **Verify the result.** Check the effective firewall policy, counters or logs and IPv4/IPv6 coverage. Confirm that local readings remain fresh and that necessary device functions, alerts and local reconnection still work. Monitor over time for a recurring, short-interval disconnect/reconnect pattern — a possible watchdog signature (see above), distinct from an occasional, irregular reconnect that happens for ordinary network reasons. If you see a recurring pattern, do not reflexively restore internet access as an automatic fix — that re-exposes the device to firmware updates. Pause, confirm whether the device's actual function (not just its network connection) is affected, weigh whether the device is safety- or essential-function-related, and make a deliberate decision about whether continued isolation is appropriate. Do not trigger a firmware update to test the block.
5. **Keep the protection in place.** Document the rule and check it after router/configuration changes. Review firmware security advisories and release notes independently. Only restore internet access after making an informed decision; reconnecting may itself trigger a pending automatic update.

## Example firewall policy (router-independent)

| Source | Destination | Action |
| --- | --- | --- |
| Appliance | Internet/WAN (IPv4 and IPv6 as applicable) | Deny all |
| Internet/WAN | Appliance | Deny, including any applicable forwarding or existing session paths |
| Trusted local controller | Appliance | Allow required LAN traffic and replies |

On UniFi, a device-scoped Internal-to-External block rule, combined with the appropriate inbound policy and a DHCP reservation if matching by IP, is one way to implement this. Router versions differ; use the equivalent supported controls on your own network and verify their actual effect. Blocking DNS or a single port alone is not equivalent to full internet isolation.

## What we tested

On 2 November 2026, our Toshiba GR-RF900WI-PMV(06)-MG (Vietnam, TSmartLife, LAN V3) was tested with WAN access blocked. All 19 monitored LAN sensors remained available during the test, and reloading the Home Assistant integration re-authenticated using its cached local credentials without cloud access. On 24 November, the active firewall rule and fresh local temperature/door readings were verified again; the available HA history showed continued operation with occasional availability blips. This is one physical unit, not a guarantee for other models. The project's refrigerator integration is monitoring-oriented, not a demonstration of every possible local control function.

## Limitations and trade-offs

- Manufacturer remote-app functions, cloud notifications and other internet-dependent features may stop working. Some devices may behave poorly offline or require cloud services to function. Verify essential and safety-related functions; do not isolate equipment if that would compromise them.
- Some devices reportedly show a recurring disconnect/reconnect pattern, consistent with a cloud-connectivity watchdog, when they cannot reach the manufacturer's cloud (see above) — this is not confirmed as an actual device reboot in every report, and is not true of every device, but is a real possibility worth checking for. If it happens on your device, treat it as a sign that full isolation may be unsuitable for that specific device, and decide deliberately rather than automatically reconnecting it to the internet — restoring access also re-exposes the device to a pending firmware update.
- Network isolation prevents internet-delivered updates through the blocked paths; it does not prevent previously downloaded firmware, locally delivered updates or an independent connection. It does not downgrade firmware or restore removed LAN functionality.
- Security patches also cannot arrive through the blocked connection. Review relevant advisories and make informed, owner-approved maintenance decisions.
- Initial cloud credential provisioning may still be required. Do not factory-reset a working appliance merely to test isolation.
- If your router cannot separate WAN access from local communication, use suitable device-specific firewall or IoT network controls instead.

## Help the community

Please share the appliance model, market, firmware version (if known), whether local operation survived internet isolation, and any observed side effects. Redact tokens, keys, serial numbers, private addresses and other sensitive information.

A native automatic-update switch or reliable selective OTA filtering would be useful alternatives where available. Our broader [Universal Appliance Local Control project](https://github.com/jaspweowaale/universal-appliance-local-control) explores owner-controlled firmware management; selective OTA protection is a research goal, not a shipped guarantee.
