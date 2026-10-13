"""Offline tests for the onboarding helper -- no real credentials, no
network access, no TSmartLife cloud contact. All cloud interaction is
mocked.
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

from toshiba_tsmartlife_local.onboard import (
    REQUIRED_ENV_VARS,
    OnboardingError,
    _read_app_constants,
    fetch_lan_credentials,
)

FAKE_ENV = {
    "TSMARTLIFE_APP_ID": "test_only_app_id_not_real",
    "TSMARTLIFE_APP_KEY": "test_only_app_key_not_real",
    "TSMARTLIFE_IOT_KEY": "test_only_iot_key_not_real",
    "TSMARTLIFE_HMAC_KEY": "test_only_hmac_key_not_real",
}


class TestReadAppConstants:
    def test_raises_when_all_missing(self) -> None:
        with patch.dict(os.environ, {}, clear=True), pytest.raises(
            OnboardingError, match="Missing required environment variable",
        ):
            _read_app_constants()

    def test_raises_when_partially_missing(self) -> None:
        partial = dict(FAKE_ENV)
        del partial["TSMARTLIFE_HMAC_KEY"]
        with patch.dict(os.environ, partial, clear=True), pytest.raises(
            OnboardingError, match="TSMARTLIFE_HMAC_KEY",
        ):
            _read_app_constants()

    def test_succeeds_when_all_present(self) -> None:
        with patch.dict(os.environ, FAKE_ENV, clear=True):
            result = _read_app_constants()
        assert result == FAKE_ENV
        assert set(result) == set(REQUIRED_ENV_VARS)


class TestFetchLanCredentials:
    @pytest.mark.asyncio
    async def test_login_failure_raises(self) -> None:
        cloud = Mock()
        cloud.login = AsyncMock(return_value=False)
        with pytest.raises(OnboardingError, match="login failed"):
            await fetch_lan_credentials(cloud, device_sn="SN123", device_id=None)

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
