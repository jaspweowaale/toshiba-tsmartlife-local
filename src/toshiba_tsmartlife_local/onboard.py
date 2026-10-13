"""TSmartLife LAN-credential onboarding helper.

Logs in to the TSmartLife cloud with the OWNER's own account (never stored
by this tool), finds their appliance, and retrieves the device-specific
LAN ``token``/``key`` pair that the separate ``midea_ac_lan`` Home
Assistant integration needs for local-only operation afterward.

This module does **not** hardcode, store, or transmit anywhere any of:
  * the shared TSmartLife application constants (app_id/app_key/iot_key/
    hmac_key) -- these must be supplied via environment variables, see
    ``docs/TOKEN_ONBOARDING.md``;
  * the user's password (read via a hidden prompt, held in memory only for
    the duration of one `login()` call, never written to disk or logged);
  * the resulting device token/key beyond printing them once to stdout for
    the user to copy into Home Assistant themselves.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import os
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from midealan.cloud import MideaCloud

REQUIRED_ENV_VARS = (
    "TSMARTLIFE_APP_ID",
    "TSMARTLIFE_APP_KEY",
    "TSMARTLIFE_IOT_KEY",
    "TSMARTLIFE_HMAC_KEY",
)


class OnboardingError(RuntimeError):
    """Raised for any onboarding failure with a user-facing message."""


def _read_app_constants() -> dict[str, str]:
    """Read the 4 shared TSmartLife app-level constants from the environment.

    These are NOT per-user secrets -- they are the same 4 values for every
    TSmartLife installation, baked into the app itself. See
    docs/TOKEN_ONBOARDING.md for exactly why this project cannot ship them
    pre-filled and what that means for you.
    """
    missing = [v for v in REQUIRED_ENV_VARS if not os.environ.get(v)]
    if missing:
        raise OnboardingError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ".\nSee docs/TOKEN_ONBOARDING.md for what these are and why "
            "this tool cannot provide them for you.",
        )
    return {v: os.environ[v] for v in REQUIRED_ENV_VARS}


def build_cloud(
    app_constants: dict[str, str],
    account: str,
    password: str,
) -> MideaCloud:
    """Construct a TSmartLifeCloud client with the given app constants.

    Mutates midealan.cloud.SUPPORTED_CLOUDS["TSmartLife"] in-process for the
    lifetime of this interpreter -- the same mechanism midea-lan's own test
    suite uses, not a private API we invented.
    """
    from aiohttp import ClientSession
    from midealan.cloud import SUPPORTED_CLOUDS, get_midea_cloud

    SUPPORTED_CLOUDS["TSmartLife"].update(
        {
            "app_id": app_constants["TSMARTLIFE_APP_ID"],
            "app_key": app_constants["TSMARTLIFE_APP_KEY"],
            "iot_key": app_constants["TSMARTLIFE_IOT_KEY"],
            "hmac_key": app_constants["TSMARTLIFE_HMAC_KEY"],
        },
    )
    session = ClientSession()
    return get_midea_cloud(
        "TSmartLife",
        session=session,
        account=account,
        password=password,
    )


async def fetch_lan_credentials(
    cloud: MideaCloud,
    device_sn: str | None,
    device_id: int | None,
) -> dict[int, dict[str, Any]]:
    """Log in, resolve the appliance, and return its LAN token/key options.

    Returns the raw {method_number: {"token": ..., "key": ...}} mapping
    from get_cloud_keys() -- some clouds offer more than one method; the
    caller should try each in order (exactly as Stage 4M of the original
    investigation did) since only one may actually authenticate over LAN.
    """
    if not await cloud.login():
        raise OnboardingError(
            "TSmartLife cloud login failed. Check your account email/"
            "password, and confirm the 4 TSMARTLIFE_* environment "
            "variables are correct (a wrong app_id/app_key will also "
            "manifest as a login failure, not a clearer error).",
        )

    resolved_id = device_id
    if resolved_id is None:
        if not device_sn:
            raise OnboardingError("Provide either --device-id or --device-sn.")
        appliances = await cloud.list_appliances(home_id=None)
        if not appliances:
            raise OnboardingError(
                "Login succeeded but the account has no appliances, or the "
                "cloud did not return a list. Confirm this account is the "
                "one actually paired with the fridge in the TSmartLife app.",
            )
        match = next(
            (aid for aid, info in appliances.items() if info.get("sn") == device_sn),
            None,
        )
        if match is None:
            known = ", ".join(str(info.get("sn")) for info in appliances.values())
            raise OnboardingError(
                f"No appliance with SN {device_sn!r} found on this account. "
                f"SNs visible to this account: {known or '(none)'}",
            )
        resolved_id = match

    keys = await cloud.get_cloud_keys(resolved_id)
    if not keys:
        raise OnboardingError(
            "Login and appliance lookup succeeded, but the cloud returned "
            "no LAN token/key for this appliance. This has not been seen "
            "in testing -- please report the exact (sanitized) error.",
        )
    return keys


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="toshiba-tsmartlife-onboard",
        description=__doc__,
    )
    parser.add_argument("--username", required=True, help="Your TSmartLife account email.")
    parser.add_argument(
        "--device-sn",
        default=None,
        help="Your appliance's serial number (printed inside the door). "
        "Alternative to --device-id.",
    )
    parser.add_argument(
        "--device-id",
        type=int,
        default=None,
        help="Numeric appliance ID, if already known (e.g. from LAN discovery).",
    )
    return parser.parse_args(argv)


async def _run(argv: list[str]) -> int:
    args = _parse_args(argv)
    try:
        app_constants = _read_app_constants()
    except OnboardingError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    password = getpass.getpass(f"TSmartLife password for {args.username}: ")
    cloud = build_cloud(app_constants, args.username, password)
    del password  # drop the local reference as soon as it's been used

    try:
        keys = await fetch_lan_credentials(cloud, args.device_sn, args.device_id)
    except OnboardingError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
        await cloud._session.close()

    print("\nSuccess. LAN credential candidate(s) for this appliance:\n")
    for method, kv in sorted(keys.items()):
        print(f"  Method {method}:")
        print(f"    token = {kv['token']}")
        print(f"    key   = {kv['key']}")
    print(
        "\nIf more than one method is listed, try each in midea_ac_lan's "
        "'Configure manually' config-flow step in order -- only one may "
        "actually authenticate over LAN for your specific device.\n"
        "These values are specific to YOUR appliance. Do not share them "
        "publicly, and do not commit them to any repository.",
    )
    return 0


def main(argv: list[str] | None = None) -> None:
    """CLI entry point (see pyproject.toml's [project.scripts])."""
    sys.exit(asyncio.run(_run(sys.argv[1:] if argv is None else argv)))


if __name__ == "__main__":
    main()
