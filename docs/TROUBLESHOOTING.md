# Troubleshooting

**Windows: "running scripts is disabled on this system" when activating
the virtual environment** — PowerShell blocks `.venv\Scripts\Activate.ps1`
by default on most fresh Windows installs; this is a Windows/PowerShell
default, not specific to this project. Fix, in an **admin** PowerShell
window, once per machine:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then retry the activation command in a normal (non-admin) PowerShell
window. If you'd rather not change the execution policy at all, use
`cmd.exe` instead and run `.venv\Scripts\activate.bat`, which isn't
affected by this setting.

**Windows: `py` is not recognized** — some Windows Python installs don't
register the `py` launcher (e.g. a Microsoft Store install, or an older
installer run without "Add to PATH"). Use `python` instead of `py` for
every command in this guide if that happens (`python -m venv .venv`,
etc.) — they're equivalent once Python is actually on your `PATH`.

**"Missing required environment variable(s)"** — one or more of the 4
`TSMARTLIFE_*` variables isn't set. See `docs/TOKEN_ONBOARDING.md` — if
you don't have these values, that document explains the current state
honestly; this isn't a bug to work around.

**"TSmartLife cloud login failed"** — this error is deliberately generic
because the underlying cloud API does not distinguish "wrong password"
from "wrong app_id/app_key" in its response. Double-check your email and
password first (log into the official app to confirm they still work),
then double-check the 4 environment variables are exactly what you were
given, with no extra whitespace.

**"No appliance with SN ... found on this account"** — the SN must match
exactly what the TSmartLife app shows for your device (check Device
Information in the app), and the account you're logging in with here must
be the same account that device is paired to in that app.

**It worked, but `midea_ac_lan` still won't connect** — the token/key this
tool prints are for Protocol V3. Confirm in `midea_ac_lan`'s config flow
that you're using the "Configure manually" path with the correct
`device_type` (`0xCA` for this refrigerator family) and that your
appliance is reachable on the same local network/VLAN as your Home
Assistant instance (local-only VLANs that block east-west traffic between
IoT and server segments are a common, unrelated cause of "can't connect"
that looks identical to a bad token).

**Everything worked once, but stopped working after a router change /
Wi-Fi password change** — the appliance's own Wi-Fi reconnects
independently of this tool; if it successfully got a new IP and rejoined
your LAN, `midea_ac_lan` should reconnect on its own. If the appliance
itself needs to be re-paired to Wi-Fi (e.g. after a full factory reset),
you likely need to redo that through the official TSmartLife app, then
re-run this tool's onboarding step once more — the LAN token/key are not
guaranteed to survive a full appliance Wi-Fi re-pair.

**I don't see this error listed here** — please open an issue with the
exact (sanitized — no password, no token/key, no account email) error
text and which step you were on.
