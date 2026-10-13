"""Offline tests for the onboarding helper -- no real credentials, no
network access, no TSmartLife cloud contact. All cloud interaction is
mocked.
"""

from __future__ import annotations

import json
import os
import stat
from unittest.mock import AsyncMock, Mock, patch

import pytest

from toshiba_tsmartlife_local.onboard import (
    REQUIRED_ENV_VARS,
    OnboardingError,
    _read_app_constants,
    _read_app_constants_from_file,
    _write_output_file,
    build_cloud,
    fetch_lan_credentials,
)

FAKE_ENV = {
    "TSMARTLIFE_APP_ID": "test_only_app_id_not_real",
    "TSMARTLIFE_APP_KEY": "test_only_app_key_not_real",
    "TSMARTLIFE_IOT_KEY": "test_only_iot_key_not_real",
    "TSMARTLIFE_HMAC_KEY": "test_only_hmac_key_not_real",
}

FAKE_CONFIG_FILE_CONTENT = {
    "app_id": "file_app_id_not_real",
    "app_key": "file_app_key_not_real",
    "iot_key": "file_iot_key_not_real",
    "hmac_key": "file_hmac_key_not_real",
}


class TestReadAppConstants:
    def test_raises_when_all_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True), pytest.raises(
            OnboardingError, match="Missing required TSmartLife app configuration",
        ):
            _read_app_constants(config_file=None)

    def test_raises_when_partially_missing(self) -> None:
        partial = dict(FAKE_ENV)
        del partial["TSMARTLIFE_HMAC_KEY"]
        with patch.dict(os.environ, partial, clear=True), pytest.raises(
            OnboardingError, match="TSMARTLIFE_HMAC_KEY",
        ):
            _read_app_constants(config_file=None)

    def test_succeeds_when_all_present_via_env(self) -> None:
        with patch.dict(os.environ, FAKE_ENV, clear=True):
            result = _read_app_constants(config_file=None)
        assert result == FAKE_ENV
        assert set(result) == set(REQUIRED_ENV_VARS)

    def test_config_file_arg_takes_precedence_over_env(self, tmp_path) -> None:
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(FAKE_CONFIG_FILE_CONTENT))
        with patch.dict(os.environ, FAKE_ENV, clear=True):
            result = _read_app_constants(config_file=str(config_path))
        assert result["TSMARTLIFE_APP_ID"] == "file_app_id_not_real"

    def test_config_file_env_var_used_when_no_arg(self, tmp_path) -> None:
        config_path = tmp_path / "config.json"
        config_path.write_text(json.dumps(FAKE_CONFIG_FILE_CONTENT))
        with patch.dict(
            os.environ, {"TSMARTLIFE_CONFIG_FILE": str(config_path)}, clear=True,
        ):
            result = _read_app_constants(config_file=None)
        assert result["TSMARTLIFE_HMAC_KEY"] == "file_hmac_key_not_real"


class TestReadAppConstantsFromFile:
    def test_missing_file_raises(self, tmp_path) -> None:
        with pytest.raises(OnboardingError, match="Could not read config file"):
            _read_app_constants_from_file(tmp_path / "nope.json")

    def test_invalid_json_raises(self, tmp_path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("{not valid json")
        with pytest.raises(OnboardingError, match="not valid JSON"):
            _read_app_constants_from_file(path)

    def test_non_object_json_raises(self, tmp_path) -> None:
        path = tmp_path / "list.json"
        path.write_text("[1, 2, 3]")
        with pytest.raises(OnboardingError, match="JSON object"):
            _read_app_constants_from_file(path)

    def test_missing_keys_raises(self, tmp_path) -> None:
        path = tmp_path / "partial.json"
        path.write_text(json.dumps({"app_id": "x"}))
        with pytest.raises(OnboardingError, match="missing required key"):
            _read_app_constants_from_file(path)

    def test_valid_file_returns_env_shaped_dict(self, tmp_path) -> None:
        path = tmp_path / "good.json"
        path.write_text(json.dumps(FAKE_CONFIG_FILE_CONTENT))
        result = _read_app_constants_from_file(path)
        assert result == {
            "TSMARTLIFE_APP_ID": "file_app_id_not_real",
            "TSMARTLIFE_APP_KEY": "file_app_key_not_real",
            "TSMARTLIFE_IOT_KEY": "file_iot_key_not_real",
            "TSMARTLIFE_HMAC_KEY": "file_hmac_key_not_real",
        }

    @pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits only")
    def test_warns_when_world_readable(self, tmp_path, capsys) -> None:
        path = tmp_path / "loose.json"
        path.write_text(json.dumps(FAKE_CONFIG_FILE_CONTENT))
        path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IROTH)
        _read_app_constants_from_file(path)
        assert "readable by other users" in capsys.readouterr().err

    @pytest.mark.skipif(os.name == "nt", reason="POSIX permission bits only")
    def test_no_warning_when_owner_only(self, tmp_path, capsys) -> None:
        path = tmp_path / "tight.json"
        path.write_text(json.dumps(FAKE_CONFIG_FILE_CONTENT))
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        _read_app_constants_from_file(path)
        assert capsys.readouterr().err == ""


class TestWriteOutputFile:
    def test_writes_json_and_restricts_permissions(self, tmp_path) -> None:
        out_path = tmp_path / "result.json"
        _write_output_file(str(out_path), {1: {"token": "tok", "key": "key"}})
        assert json.loads(out_path.read_text()) == {"1": {"token": "tok", "key": "key"}}
        if os.name != "nt":
            mode = stat.S_IMODE(out_path.stat().st_mode)
            assert mode == stat.S_IRUSR | stat.S_IWUSR


class TestBuildCloud:
    @pytest.mark.asyncio
    async def test_blank_app_id_raises_onboarding_error_not_library_exception(self) -> None:
        blank = dict.fromkeys(REQUIRED_ENV_VARS, "")
        with pytest.raises(OnboardingError, match="incomplete or malformed"):
            build_cloud(blank, "account", "password")

    @pytest.mark.asyncio
    async def test_valid_constants_construct_successfully(self) -> None:
        cloud = build_cloud(FAKE_ENV, "account", "password")
        try:
            assert cloud is not None
        finally:
            await cloud._session.close()


class TestFetchLanCredentials:
    @pytest.mark.asyncio
    async def test_login_failure_raises(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(return_value=False)
        with pytest.raises(OnboardingError, match="login failed"):
            await fetch_lan_credentials(cloud, device_sn="SN123", device_id=None)

    @pytest.mark.asyncio
    async def test_login_exception_is_wrapped(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(side_effect=ConnectionError("network unreachable"))
        with pytest.raises(OnboardingError, match="unexpected error"):
            await fetch_lan_credentials(cloud, device_sn="SN123", device_id=None)

    @pytest.mark.asyncio
    async def test_list_appliances_exception_is_wrapped(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(return_value=True)
        cloud.list_appliances = AsyncMock(side_effect=TimeoutError("timed out"))
        with pytest.raises(OnboardingError, match="Could not list appliances"):
            await fetch_lan_credentials(cloud, device_sn="SN123", device_id=None)

    @pytest.mark.asyncio
    async def test_get_cloud_keys_exception_is_wrapped(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(return_value=True)
        cloud.get_cloud_keys = AsyncMock(side_effect=ValueError("bad response"))
        with pytest.raises(OnboardingError, match="Could not retrieve LAN keys"):
            await fetch_lan_credentials(cloud, device_sn=None, device_id=42)

    @pytest.mark.asyncio
    async def test_blank_sn_treated_as_missing(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(return_value=True)
        with pytest.raises(OnboardingError, match="device-id or --device-sn"):
            await fetch_lan_credentials(cloud, device_sn="   ", device_id=None)

    @pytest.mark.asyncio
    async def test_no_sn_or_id_raises(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(return_value=True)
        with pytest.raises(OnboardingError, match="device-id or --device-sn"):
            await fetch_lan_credentials(cloud, device_sn=None, device_id=None)

    @pytest.mark.asyncio
    async def test_resolves_device_id_directly_without_listing(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(return_value=True)
        cloud.list_appliances = AsyncMock()
        cloud.get_cloud_keys = AsyncMock(
            return_value={1: {"token": "tok", "key": "key"}},
        )
        result = await fetch_lan_credentials(cloud, device_sn=None, device_id=42)
        cloud.list_appliances.assert_not_awaited()
        cloud.get_cloud_keys.assert_awaited_once_with(42)
        assert result == {1: {"token": "tok", "key": "key"}}

    @pytest.mark.asyncio
    async def test_matches_device_by_sn(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(return_value=True)
        cloud.list_appliances = AsyncMock(
            return_value={
                111: {"sn": "OTHER_SN"},
                222: {"sn": "TARGET_SN"},
            },
        )
        cloud.get_cloud_keys = AsyncMock(
            return_value={1: {"token": "tok", "key": "key"}},
        )
        result = await fetch_lan_credentials(cloud, device_sn="TARGET_SN", device_id=None)
        cloud.get_cloud_keys.assert_awaited_once_with(222)
        assert result == {1: {"token": "tok", "key": "key"}}

    @pytest.mark.asyncio
    async def test_sn_not_found_raises_with_known_sns_listed(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(return_value=True)
        cloud.list_appliances = AsyncMock(return_value={111: {"sn": "OTHER_SN"}})
        with pytest.raises(OnboardingError, match="OTHER_SN"):
            await fetch_lan_credentials(cloud, device_sn="MISSING_SN", device_id=None)

    @pytest.mark.asyncio
    async def test_empty_appliance_list_raises(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(return_value=True)
        cloud.list_appliances = AsyncMock(return_value=None)
        with pytest.raises(OnboardingError, match="no appliances"):
            await fetch_lan_credentials(cloud, device_sn="SN123", device_id=None)

    @pytest.mark.asyncio
    async def test_empty_keys_response_raises(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(return_value=True)
        cloud.get_cloud_keys = AsyncMock(return_value={})
        with pytest.raises(OnboardingError, match="no LAN token/key"):
            await fetch_lan_credentials(cloud, device_sn=None, device_id=42)
