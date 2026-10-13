"""Offline, structural checks on the example dashboard/blueprint files.

These do not exercise Home Assistant itself (no HA test harness is a
dependency of this project) -- they only guard against the kind of plain
textual mistake that's easy to reintroduce by hand-editing YAML, and that
this project has already hit once (see door_left_open_alert.yaml's
`trigger_variables` fix).
"""

from __future__ import annotations

from pathlib import Path

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"


def _read(relative: str) -> str:
    path = EXAMPLES_DIR / relative
    assert path.is_file(), f"expected example file missing: {path}"
    return path.read_text(encoding="utf-8")


class TestDoorLeftOpenAlertBlueprint:
    """door_left_open_alert.yaml must use `trigger_variables`, not a plain
    top-level `variables:`, for any name referenced inside the `trigger:`
    block -- Home Assistant does not make a plain `variables:` block
    available to trigger templates, only to condition/action templates.
    """

    def test_uses_trigger_variables_not_plain_variables(self) -> None:
        content = _read("blueprints/door_left_open_alert.yaml")
        assert "trigger_variables:" in content
        assert "\nvariables:" not in content

    def test_delay_helper_is_defined_before_use_in_trigger(self) -> None:
        content = _read("blueprints/door_left_open_alert.yaml")
        trigger_vars_idx = content.index("trigger_variables:")
        trigger_idx = content.index("\ntrigger:")
        template_idx = content.index("states(delay_helper)")
        # trigger_variables must be declared, and the template that
        # consumes delay_helper must come from inside the trigger block.
        assert trigger_vars_idx < trigger_idx < template_idx


class TestLovelaceDashboardExample:
    """Entity-id patterns in the example dashboard must match the actual
    entity-id shape midea_ac_lan produces for device type 0xCA (confirmed
    against this project's own real production use: `sensor.<device_id>_
    refrigerator_actual_temp`, etc.) -- not an invented naming scheme.
    """

    def test_only_documented_working_entities_are_referenced(self) -> None:
        content = _read("lovelace_dashboard_example.yaml")
        expected_suffixes = [
            "refrigerator_actual_temp",
            "refrigerator_setting_temp",
            "freezer_actual_temp",
            "freezer_setting_temp",
            "flex_zone_actual_temp",
            "flex_zone_setting_temp",
            "refrigerator_door",
            "freezer_door",
        ]
        for suffix in expected_suffixes:
            assert f"YOUR_DEVICE_ID_{suffix}" in content

        # Entities explicitly documented as not working (README /
        # KNOWN_LIMITATIONS.md) must not appear on the example dashboard.
        not_claimed_working = [
            "humidity",
            "electronic_smell",
            "right_flex_zone",
            "variable_mode",
        ]
        for name in not_claimed_working:
            assert name not in content
