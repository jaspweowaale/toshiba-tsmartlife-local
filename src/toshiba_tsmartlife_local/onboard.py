"""TSmartLife LAN-credential onboarding helper.

Logs in to the TSmartLife cloud with the OWNER's own account (never stored
by this tool), finds their appliance, and retrieves the device-specific
LAN ``token``/``key`` pair that the separate ``midea_ac_lan`` (or, on
recent Home Assistant releases, the built-in "Midea") integration needs
for local-only operation afterward.

A built-in default set of the 4 shared TSmartLife app-level constants
("TSmartLife Vietnam" -- see ``vietnam_defaults.py`` and
``docs/APP_CREDENTIAL_SECURITY.md``) is used automatically if you don't
supply your own. This module still does **not** hardcode, store, or
transmit anywhere any of:
  * the user's own TSmartLife account username/password (read via a
    hidden prompt, held in memory only for the duration of one `login()`
    call, never written to disk or logged);
  * the resulting device-specific LAN token/key, beyond printing them
    once (or writing them once, if --output-file is given, with
    restrictive permissions) for the user to copy into Home Assistant
    themselves;
  * the device serial number/ID beyond what's needed to let the user
    pick their own appliance;
  * any session token or cookie.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import os
import stat
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from midealan.cloud import MideaCloud

REQUIRED_ENV_VARS = (
    "TSMARTLIFE_APP_ID",
    "TSMARTLIFE_APP_KEY",
    "TSMARTLIFE_IOT_KEY",
    "TSMARTLIFE_HMAC_KEY",
)
CONFIG_FILE_KEYS = {
    "app_id": "TSMARTLIFE_APP_ID",
    "app_key": "TSMARTLIFE_APP_KEY",
    "iot_key": "TSMARTLIFE_IOT_KEY",
    "hmac_key": "TSMARTLIFE_HMAC_KEY",
}
CONFIG_FILE_ENV_VAR = "TSMARTLIFE_CONFIG_FILE"


class OnboardingError(RuntimeError):
    """Raised for any onboarding failure with a user-facing message.

    Every code path in this module that can fail is expected to raise
    this (never a raw/unexpected exception reaching the user) -- see
    `_run`'s top-level handling for the final safety net.
    """


def _read_app_constants_from_file(path: Path) -> dict[str, str]:
    """Read the 4 app constants from a local JSON file.

    Expected shape: {"app_id": "...", "app_key": "...", "iot_key": "...",
    "hmac_key": "..."}. This is an alternative to setting 4 separate
    environment variables -- useful if you'd rather keep them in one
    file (which you must keep out of any git repository yourself; see
    docs/SECURITY_AND_PRIVACY.md).
    """
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as e:
        raise OnboardingError(f"Could not read config file {path}: {e}") from e

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise OnboardingError(f"Config file {path} is not valid JSON: {e}") from e

    if not isinstance(data, dict):
        raise OnboardingError(f"Config file {path} must contain a JSON object.")

    missing = [k for k in CONFIG_FILE_KEYS if not data.get(k)]
    if missing:
        raise OnboardingError(
            f"Config file {path} is missing required key(s): "
            + ", ".join(missing),
        )

    if os.name != "nt":
        mode = stat.S_IMODE(path.stat().st_mode)
        if mode & (stat.S_IRWXG | stat.S_IRWXO):
            print(
                f"WARNING: {path} is readable by other users on this "
                f"system (mode {oct(mode)}). Consider `chmod 600 {path}`.",
                file=sys.stderr,
            )

    return {CONFIG_FILE_KEYS[k]: data[k] for k in CONFIG_FILE_KEYS}


def _read_app_constants(config_file: str | None) -> dict[str, str]:
    """Read the 4 shared TSmartLife app-level constants.

    Precedence, highest first: --config-file argument,
    $TSMARTLIFE_CONFIG_FILE, the 4 individual TSMARTLIFE_* environment
    variables (only if *all 4* are set), then the built-in
    "TSmartLife Vietnam" default (``vietnam_defaults.VIETNAM_DEFAULT``).
    Any explicit override always wins over the built-in default -- it is
    only ever used when nothing else is supplied. These are NOT per-user
    secrets -- they are the same 4 values for every TSmartLife
    installation, baked into the app itself; see
    docs/APP_CREDENTIAL_SECURITY.md for the full classification and why
    shipping a default is considered safe to do.
    """
    path_str = config_file or os.environ.get(CONFIG_FILE_ENV_VAR)
    if path_str:
        return _read_app_constants_from_file(Path(path_str).expanduser())

    present = [v for v in REQUIRED_ENV_VARS if os.environ.get(v)]
    if present and len(present) < len(REQUIRED_ENV_VARS):
        # Some but not all 4 are set -- almost certainly a typo/partial
        # override attempt, not "no override at all". Raise rather than
        # silently falling back to the built-in default and discarding
        # the partial input the user clearly intended to use.
        missing = [v for v in REQUIRED_ENV_VARS if v not in present]
        raise OnboardingError(
            "Partial TSmartLife app configuration via environment "
            "variables: missing " + ", ".join(missing) + ". Set all 4 "
            "(to override), or none (to use the built-in default).",
        )
    if len(present) == len(REQUIRED_ENV_VARS):
        return {v: os.environ[v] for v in REQUIRED_ENV_VARS}

    from toshiba_tsmartlife_local.vietnam_defaults import VIETNAM_DEFAULT

    print(
        "Using the built-in 'TSmartLife Vietnam' app configuration default "
        "(no --config-file/$TSMARTLIFE_CONFIG_FILE/TSMARTLIFE_* env vars "
        "were supplied). See docs/APP_CREDENTIAL_SECURITY.md.",
        file=sys.stderr,
    )
    return {CONFIG_FILE_KEYS[k]: v for k, v in VIETNAM_DEFAULT.items()}


def build_cloud(
    app_constants: dict[str, str],
    account: str,
    password: str,
) -> MideaCloud:
    """Construct a TSmartLifeCloud client with the given app constants.

    Mutates midealan.cloud.SUPPORTED_CLOUDS["TSmartLife"] in-process for the
    lifetime of this interpreter -- the same mechanism midea-lan's own test
    suite uses, not a private API we invented.

    Raises OnboardingError (not the library's own ElementMissing) if the
    constants are blank/invalid, so callers never see an unexpected
    exception type.
    """
    from aiohttp import ClientSession
    from midealan.cloud import SUPPORTED_CLOUDS, get_midea_cloud
    from midealan.exceptions import ElementMissing

    SUPPORTED_CLOUDS["TSmartLife"].update(
        {
            "app_id": app_constants["TSMARTLIFE_APP_ID"],
            "app_key": app_constants["TSMARTLIFE_APP_KEY"],
            "iot_key": app_constants["TSMARTLIFE_IOT_KEY"],
            "hmac_key": app_constants["TSMARTLIFE_HMAC_KEY"],
        },
    )
    session = ClientSession()
    try:
        return get_midea_cloud(
            "TSmartLife",
            session=session,
            account=account,
            password=password,
        )
    except ElementMissing as e:
        raise OnboardingError(
            "The TSmartLife app configuration is incomplete or malformed "
            f"(library error: {e}). Double-check all 4 values are present "
            "and non-empty.",
        ) from e


def select_appliance(appliances: dict[int, dict[str, Any]]) -> int:
    """Return the appliance id to use, listing/prompting if there's more
    than one so the user never needs to already know an internal device
    ID or serial number.

    Exactly one appliance: auto-selected, no prompt. More than one: a
    numbered list (name + SN only, never the raw internal id) is printed
    and the user is asked to pick one. Raises OnboardingError on an
    invalid/empty selection rather than looping forever or guessing.
    """
    if len(appliances) == 1:
        return next(iter(appliances))

    ordered = sorted(appliances.items())
    print("\nMore than one appliance found on this account:", file=sys.stderr)
    for i, (_aid, info) in enumerate(ordered, start=1):
        name = info.get("name") or "(unnamed)"
        sn = info.get("sn") or "(unknown SN)"
        print(f"  {i}. {name}  [SN: {sn}]", file=sys.stderr)

    choice = input(f"Select device [1-{len(ordered)}]: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(ordered)):
        raise OnboardingError(
            f"Invalid selection {choice!r}; expected a number from 1 to {len(ordered)}.",
        )
    return ordered[int(choice) - 1][0]


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

    Any network/transport error from the underlying library is caught and
    re-raised as OnboardingError with a plain-language message -- callers
    should never see a raw aiohttp/asyncio traceback here.
    """
    try:
        logged_in = await cloud.login()
    except Exception as e:
        # unexpected transport/library failure into a clean, safe message
        # rather than letting a raw traceback (which could in principle
        # echo request/response internals) reach the terminal.
        raise OnboardingError(
            f"TSmartLife cloud login raised an unexpected error ({type(e).__name__}: {e}). "
            "This usually means a network problem or a cloud-side change, "
            "not a wrong password.",
        ) from e

    if not logged_in:
        raise OnboardingError(
            "TSmartLife cloud login failed. Check your account email/"
            "password, and confirm the 4 TSmartLife app configuration "
            "values are correct (a wrong app_id/app_key will also "
            "manifest as a login failure, not a clearer error).",
        )

    resolved_id = device_id
    if resolved_id is None:
        try:
            appliances = await cloud.list_appliances(home_id=None)
        except Exception as e:
            raise OnboardingError(
                f"Could not list appliances ({type(e).__name__}: {e}).",
            ) from e
        if not appliances:
            raise OnboardingError(
                "Login succeeded but the account has no appliances, or the "
                "cloud did not return a list. Confirm this account is the "
                "one actually paired with the fridge in the TSmartLife app.",
            )

        if device_sn and device_sn.strip():
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
        else:
            resolved_id = select_appliance(appliances)

    try:
        keys = await cloud.get_cloud_keys(resolved_id)
    except Exception as e:
        raise OnboardingError(
            f"Could not retrieve LAN keys ({type(e).__name__}: {e}).",
        ) from e
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
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--username",
        default=None,
        help="Your TSmartLife account email. Prompted interactively if omitted.",
    )
    parser.add_argument(
        "--device-sn",
        default=None,
        help="Your appliance's serial number (printed inside the door). "
        "Optional -- if omitted (along with --device-id), this tool lists "
        "your account's appliances and lets you pick interactively.",
    )
    parser.add_argument(
        "--device-id",
        type=int,
        default=None,
        help="Numeric appliance ID, if already known (e.g. from LAN discovery). "
        "Optional, same as --device-sn.",
    )
    parser.add_argument(
        "--config-file",
        default=None,
        help=f"Path to a JSON file with the 4 app-level constants "
        f"({sorted(CONFIG_FILE_KEYS)}). Alternative to setting "
        f"4 separate environment variables, or ${CONFIG_FILE_ENV_VAR}.",
    )
    parser.add_argument(
        "--output-file",
        default=None,
        help="Write the resulting token/key to this file (created with "
        "owner-only permissions where supported) instead of only "
        "printing to the terminal.",
    )
    return parser.parse_args(argv)


def _write_output_file(path_str: str, keys: dict[int, dict[str, Any]]) -> None:
    path = Path(path_str).expanduser()
    payload = json.dumps(keys, indent=2) + "\n"
    path.write_text(payload, encoding="utf-8")
    if os.name != "nt":
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0600: owner read/write only


async def _run(argv: list[str]) -> int:
    args = _parse_args(argv)
    try:
        app_constants = _read_app_constants(args.config_file)
    except OnboardingError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    username = args.username
    if not username:
        username = input("TSmartLife account email: ").strip()
    if not username:
        print("ERROR: username/email cannot be empty.", file=sys.stderr)
        return 2

    password = getpass.getpass(f"TSmartLife password for {username}: ")
    if not password:
        print("ERROR: password cannot be empty.", file=sys.stderr)
        return 2

    try:
        cloud = build_cloud(app_constants, username, password)
    except OnboardingError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    finally:
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
        "\nIf more than one method is listed, try each in turn in your Home "
        "Assistant integration's 'Configure manually' config-flow step "
        "(device type 0xCA, protocol V3) -- only one may actually "
        "authenticate over LAN for your specific device.\n"
        "These values are specific to YOUR appliance. Do not share them "
        "publicly, and do not commit them to any repository.",
    )
    if args.output_file:
        try:
            _write_output_file(args.output_file, keys)
        except OSError as e:
            print(f"\nWARNING: could not write {args.output_file}: {e}", file=sys.stderr)
        else:
            print(f"\nAlso written to {args.output_file} (owner-only permissions).")
    return 0


def main(argv: list[str] | None = None) -> None:
    """CLI entry point (see pyproject.toml's [project.scripts])."""
    try:
        exit_code = asyncio.run(_run(sys.argv[1:] if argv is None else argv))
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        exit_code = 130
    except Exception as e:  # noqa: BLE001 -- final safety net: never show a
        # raw traceback to the user. By this point every expected failure
        # has already been converted to OnboardingError and handled in
        # _run(); reaching here means something truly unanticipated
        # happened, so fail safely rather than risk echoing internals.
        print(
            f"ERROR: unexpected failure ({type(e).__name__}: {e}). "
            "This is not one of the known failure modes documented in "
            "docs/TROUBLESHOOTING.md -- please report it (sanitized).",
            file=sys.stderr,
        )
        exit_code = 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
