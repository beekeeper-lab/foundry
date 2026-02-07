"""Tests for foundry_app.ui.screens.builder.wizard_pages.architecture_page."""

import pytest
from PySide6.QtWidgets import QApplication

from foundry_app.core.models import (
    ArchitectureConfig,
    ArchitecturePattern,
    CloudProvider,
)
from foundry_app.ui.screens.builder.wizard_pages.architecture_page import (
    CLOUD_DESCRIPTIONS,
    PATTERN_DESCRIPTIONS,
    ArchitectureCard,
    ArchitectureCloudPage,
)

_app = QApplication.instance() or QApplication([])


# ---------------------------------------------------------------------------
# ArchitectureCard — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def card():
    c = ArchitectureCard("microservices", "Microservices", "Independently deployable services")
    yield c
    c.close()


class TestCardConstruction:
    def test_creates_without_error(self, card):
        assert card is not None

    def test_item_id(self, card):
        assert card.item_id == "microservices"

    def test_display_name(self, card):
        assert card.display_name == "Microservices"

    def test_initially_not_selected(self, card):
        assert card.is_selected is False

    def test_object_name(self, card):
        assert card.objectName() == "arch-card"


# ---------------------------------------------------------------------------
# ArchitectureCard — selection
# ---------------------------------------------------------------------------

class TestCardSelection:
    def test_select_via_property(self, card):
        card.is_selected = True
        assert card.is_selected is True

    def test_deselect_via_property(self, card):
        card.is_selected = True
        card.is_selected = False
        assert card.is_selected is False

    def test_toggled_signal_emitted_on_select(self, card):
        received = []
        card.toggled.connect(lambda iid, checked: received.append((iid, checked)))
        card.is_selected = True
        assert len(received) == 1
        assert received[0] == ("microservices", True)

    def test_toggled_signal_emitted_on_deselect(self, card):
        card.is_selected = True
        received = []
        card.toggled.connect(lambda iid, checked: received.append((iid, checked)))
        card.is_selected = False
        assert len(received) == 1
        assert received[0] == ("microservices", False)


# ---------------------------------------------------------------------------
# ArchitectureCard — empty description
# ---------------------------------------------------------------------------

class TestCardEmptyDescription:
    def test_empty_description_ok(self):
        c = ArchitectureCard("test-id", "Test", "")
        assert c.item_id == "test-id"
        c.close()


# ---------------------------------------------------------------------------
# ArchitectureCloudPage — construction
# ---------------------------------------------------------------------------

@pytest.fixture()
def page():
    p = ArchitectureCloudPage()
    yield p
    p.close()


class TestPageConstruction:
    def test_creates_without_error(self, page):
        assert page is not None

    def test_has_5_pattern_cards(self, page):
        assert len(page.pattern_cards) == 5

    def test_has_4_cloud_cards(self, page):
        assert len(page.cloud_cards) == 4

    def test_initially_valid(self, page):
        # Page is always valid (optional)
        assert page.is_valid() is True

    def test_no_patterns_selected_initially(self, page):
        assert page.selected_pattern_count() == 0

    def test_no_clouds_selected_initially(self, page):
        assert page.selected_cloud_count() == 0


# ---------------------------------------------------------------------------
# ArchitectureCloudPage — pattern card IDs
# ---------------------------------------------------------------------------

class TestPatternCardIds:
    def test_monolith_card_present(self, page):
        assert "monolith" in page.pattern_cards

    def test_modular_monolith_card_present(self, page):
        assert "modular-monolith" in page.pattern_cards

    def test_microservices_card_present(self, page):
        assert "microservices" in page.pattern_cards

    def test_serverless_card_present(self, page):
        assert "serverless" in page.pattern_cards

    def test_event_driven_card_present(self, page):
        assert "event-driven" in page.pattern_cards

    def test_all_pattern_ids_match_enum(self, page):
        expected = {p.value for p in ArchitecturePattern}
        assert set(page.pattern_cards.keys()) == expected


# ---------------------------------------------------------------------------
# ArchitectureCloudPage — cloud card IDs
# ---------------------------------------------------------------------------

class TestCloudCardIds:
    def test_aws_card_present(self, page):
        assert "aws" in page.cloud_cards

    def test_azure_card_present(self, page):
        assert "azure" in page.cloud_cards

    def test_gcp_card_present(self, page):
        assert "gcp" in page.cloud_cards

    def test_self_hosted_card_present(self, page):
        assert "self-hosted" in page.cloud_cards

    def test_all_cloud_ids_match_enum(self, page):
        expected = {c.value for c in CloudProvider}
        assert set(page.cloud_cards.keys()) == expected


# ---------------------------------------------------------------------------
# ArchitectureCloudPage — pattern selection
# ---------------------------------------------------------------------------

class TestPatternSelection:
    def test_select_one_pattern(self, page):
        page.pattern_cards["microservices"].is_selected = True
        assert page.selected_pattern_count() == 1

    def test_select_multiple_patterns(self, page):
        page.pattern_cards["microservices"].is_selected = True
        page.pattern_cards["event-driven"].is_selected = True
        assert page.selected_pattern_count() == 2

    def test_deselect_pattern(self, page):
        page.pattern_cards["microservices"].is_selected = True
        page.pattern_cards["microservices"].is_selected = False
        assert page.selected_pattern_count() == 0

    def test_page_still_valid_with_no_patterns(self, page):
        assert page.is_valid() is True

    def test_selection_changed_signal_emitted(self, page):
        received = []
        page.selection_changed.connect(lambda: received.append(True))
        page.pattern_cards["monolith"].is_selected = True
        assert len(received) >= 1


# ---------------------------------------------------------------------------
# ArchitectureCloudPage — cloud selection
# ---------------------------------------------------------------------------

class TestCloudSelection:
    def test_select_one_cloud(self, page):
        page.cloud_cards["aws"].is_selected = True
        assert page.selected_cloud_count() == 1

    def test_select_multiple_clouds(self, page):
        page.cloud_cards["aws"].is_selected = True
        page.cloud_cards["gcp"].is_selected = True
        assert page.selected_cloud_count() == 2

    def test_deselect_cloud(self, page):
        page.cloud_cards["azure"].is_selected = True
        page.cloud_cards["azure"].is_selected = False
        assert page.selected_cloud_count() == 0

    def test_page_still_valid_with_no_clouds(self, page):
        assert page.is_valid() is True

    def test_cloud_selection_changed_signal(self, page):
        received = []
        page.selection_changed.connect(lambda: received.append(True))
        page.cloud_cards["aws"].is_selected = True
        assert len(received) >= 1


# ---------------------------------------------------------------------------
# ArchitectureCloudPage — mixed selection
# ---------------------------------------------------------------------------

class TestMixedSelection:
    def test_patterns_and_clouds_independent(self, page):
        page.pattern_cards["serverless"].is_selected = True
        page.cloud_cards["aws"].is_selected = True
        assert page.selected_pattern_count() == 1
        assert page.selected_cloud_count() == 1

    def test_deselect_pattern_keeps_cloud(self, page):
        page.pattern_cards["serverless"].is_selected = True
        page.cloud_cards["aws"].is_selected = True
        page.pattern_cards["serverless"].is_selected = False
        assert page.selected_pattern_count() == 0
        assert page.selected_cloud_count() == 1

    def test_deselect_cloud_keeps_pattern(self, page):
        page.pattern_cards["serverless"].is_selected = True
        page.cloud_cards["aws"].is_selected = True
        page.cloud_cards["aws"].is_selected = False
        assert page.selected_pattern_count() == 1
        assert page.selected_cloud_count() == 0


# ---------------------------------------------------------------------------
# ArchitectureCloudPage — get_architecture_config
# ---------------------------------------------------------------------------

class TestGetConfig:
    def test_empty_config_when_nothing_selected(self, page):
        config = page.get_architecture_config()
        assert isinstance(config, ArchitectureConfig)
        assert config.patterns == []
        assert config.cloud_providers == []

    def test_config_contains_selected_patterns(self, page):
        page.pattern_cards["microservices"].is_selected = True
        page.pattern_cards["event-driven"].is_selected = True
        config = page.get_architecture_config()
        pattern_values = {p.value for p in config.patterns}
        assert pattern_values == {"microservices", "event-driven"}

    def test_config_contains_selected_clouds(self, page):
        page.cloud_cards["aws"].is_selected = True
        page.cloud_cards["gcp"].is_selected = True
        config = page.get_architecture_config()
        cloud_values = {c.value for c in config.cloud_providers}
        assert cloud_values == {"aws", "gcp"}

    def test_config_excludes_unselected(self, page):
        page.pattern_cards["microservices"].is_selected = True
        config = page.get_architecture_config()
        assert len(config.patterns) == 1
        assert config.patterns[0] == ArchitecturePattern.MICROSERVICES

    def test_config_patterns_are_enum_values(self, page):
        page.pattern_cards["monolith"].is_selected = True
        config = page.get_architecture_config()
        assert all(isinstance(p, ArchitecturePattern) for p in config.patterns)

    def test_config_clouds_are_enum_values(self, page):
        page.cloud_cards["azure"].is_selected = True
        config = page.get_architecture_config()
        assert all(isinstance(c, CloudProvider) for c in config.cloud_providers)

    def test_mixed_config(self, page):
        page.pattern_cards["serverless"].is_selected = True
        page.cloud_cards["aws"].is_selected = True
        page.cloud_cards["self-hosted"].is_selected = True
        config = page.get_architecture_config()
        assert len(config.patterns) == 1
        assert len(config.cloud_providers) == 2


# ---------------------------------------------------------------------------
# ArchitectureCloudPage — set_architecture_config
# ---------------------------------------------------------------------------

class TestSetConfig:
    def test_restores_patterns(self, page):
        config = ArchitectureConfig(
            patterns=[ArchitecturePattern.MICROSERVICES, ArchitecturePattern.SERVERLESS],
        )
        page.set_architecture_config(config)
        assert page.pattern_cards["microservices"].is_selected is True
        assert page.pattern_cards["serverless"].is_selected is True
        assert page.pattern_cards["monolith"].is_selected is False

    def test_restores_clouds(self, page):
        config = ArchitectureConfig(
            cloud_providers=[CloudProvider.AWS, CloudProvider.GCP],
        )
        page.set_architecture_config(config)
        assert page.cloud_cards["aws"].is_selected is True
        assert page.cloud_cards["gcp"].is_selected is True
        assert page.cloud_cards["azure"].is_selected is False

    def test_clears_previous_selections(self, page):
        page.pattern_cards["monolith"].is_selected = True
        page.cloud_cards["aws"].is_selected = True

        config = ArchitectureConfig(
            patterns=[ArchitecturePattern.SERVERLESS],
            cloud_providers=[CloudProvider.GCP],
        )
        page.set_architecture_config(config)
        assert page.pattern_cards["monolith"].is_selected is False
        assert page.cloud_cards["aws"].is_selected is False
        assert page.pattern_cards["serverless"].is_selected is True
        assert page.cloud_cards["gcp"].is_selected is True

    def test_empty_config_clears_all(self, page):
        page.pattern_cards["monolith"].is_selected = True
        page.cloud_cards["aws"].is_selected = True

        page.set_architecture_config(ArchitectureConfig())
        assert page.selected_pattern_count() == 0
        assert page.selected_cloud_count() == 0


# ---------------------------------------------------------------------------
# ArchitectureCloudPage — round-trip
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_get_set_get_patterns(self, page):
        page.pattern_cards["microservices"].is_selected = True
        page.pattern_cards["event-driven"].is_selected = True
        original = page.get_architecture_config()

        # Reset
        for card in page.pattern_cards.values():
            card.is_selected = False

        page.set_architecture_config(original)
        restored = page.get_architecture_config()

        assert set(p.value for p in restored.patterns) == set(
            p.value for p in original.patterns
        )

    def test_get_set_get_clouds(self, page):
        page.cloud_cards["aws"].is_selected = True
        page.cloud_cards["azure"].is_selected = True
        original = page.get_architecture_config()

        # Reset
        for card in page.cloud_cards.values():
            card.is_selected = False

        page.set_architecture_config(original)
        restored = page.get_architecture_config()

        assert set(c.value for c in restored.cloud_providers) == set(
            c.value for c in original.cloud_providers
        )

    def test_full_roundtrip(self, page):
        page.pattern_cards["serverless"].is_selected = True
        page.pattern_cards["modular-monolith"].is_selected = True
        page.cloud_cards["gcp"].is_selected = True
        page.cloud_cards["self-hosted"].is_selected = True
        original = page.get_architecture_config()

        # Reset all
        for card in page.pattern_cards.values():
            card.is_selected = False
        for card in page.cloud_cards.values():
            card.is_selected = False

        page.set_architecture_config(original)
        restored = page.get_architecture_config()

        assert len(restored.patterns) == 2
        assert len(restored.cloud_providers) == 2

    def test_empty_roundtrip(self, page):
        config = page.get_architecture_config()
        page.set_architecture_config(config)
        restored = page.get_architecture_config()
        assert restored.patterns == []
        assert restored.cloud_providers == []


# ---------------------------------------------------------------------------
# Description dictionaries completeness
# ---------------------------------------------------------------------------

class TestDescriptions:
    def test_all_patterns_have_descriptions(self):
        for pattern in ArchitecturePattern:
            assert pattern.value in PATTERN_DESCRIPTIONS, (
                f"Missing description for pattern: {pattern.value}"
            )

    def test_all_clouds_have_descriptions(self):
        for provider in CloudProvider:
            assert provider.value in CLOUD_DESCRIPTIONS, (
                f"Missing description for provider: {provider.value}"
            )

    def test_pattern_descriptions_are_tuples(self):
        for pid, desc in PATTERN_DESCRIPTIONS.items():
            assert isinstance(desc, tuple), f"{pid} description is not a tuple"
            assert len(desc) == 2, f"{pid} description tuple has {len(desc)} elements"

    def test_cloud_descriptions_are_tuples(self):
        for cid, desc in CLOUD_DESCRIPTIONS.items():
            assert isinstance(desc, tuple), f"{cid} description is not a tuple"
            assert len(desc) == 2, f"{cid} description tuple has {len(desc)} elements"

    def test_pattern_descriptions_nonempty(self):
        for pid, (name, desc) in PATTERN_DESCRIPTIONS.items():
            assert len(name) > 0, f"{pid} has empty display name"
            assert len(desc) > 0, f"{pid} has empty description"

    def test_cloud_descriptions_nonempty(self):
        for cid, (name, desc) in CLOUD_DESCRIPTIONS.items():
            assert len(name) > 0, f"{cid} has empty display name"
            assert len(desc) > 0, f"{cid} has empty description"


# ---------------------------------------------------------------------------
# Model integration
# ---------------------------------------------------------------------------

class TestModelIntegration:
    def test_architecture_config_default(self):
        config = ArchitectureConfig()
        assert config.patterns == []
        assert config.cloud_providers == []

    def test_architecture_config_with_values(self):
        config = ArchitectureConfig(
            patterns=[ArchitecturePattern.MONOLITH, ArchitecturePattern.MICROSERVICES],
            cloud_providers=[CloudProvider.AWS],
        )
        assert len(config.patterns) == 2
        assert len(config.cloud_providers) == 1

    def test_architecture_config_serialization(self):
        config = ArchitectureConfig(
            patterns=[ArchitecturePattern.SERVERLESS],
            cloud_providers=[CloudProvider.GCP, CloudProvider.AZURE],
        )
        data = config.model_dump()
        assert data["patterns"] == ["serverless"]
        assert set(data["cloud_providers"]) == {"gcp", "azure"}

    def test_architecture_config_deserialization(self):
        data = {
            "patterns": ["monolith", "event-driven"],
            "cloud_providers": ["aws"],
        }
        config = ArchitectureConfig.model_validate(data)
        assert len(config.patterns) == 2
        assert config.cloud_providers[0] == CloudProvider.AWS
