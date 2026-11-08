"""Validate test YAML files."""

import pytest
import voluptuous as vol
from voluptuous.humanize import validate_with_humanized_errors

from speech_to_phrase.util import yaml

from . import SETTINGS, TEST_LANGUAGES, TESTS_DIR

SHARED_LISTS_SCHEMA = vol.Schema(
    {
        # list name
        str: vol.Any(
            {
                vol.Required("range"): {
                    vol.Required("from"): int,
                    vol.Required("to"): int,
                    vol.Optional("step"): int,
                }
            },
            {
                vol.Required("multi_range"): [
                    {
                        vol.Required("from"): int,
                        vol.Required("to"): int,
                        vol.Optional("step"): int,
                    }
                ]
            },
        )
    }
)

FIXTURES_SCHEMA = vol.Schema(
    {
        vol.Required("language"): str,
        "fixtures": {
            vol.Required("entities"): [
                {
                    vol.Required("name"): vol.Any(str, [str]),
                    vol.Required("domain"): str,
                    vol.Optional("light_supports_color"): bool,
                    vol.Optional("light_supports_brightness"): bool,
                    vol.Optional("fan_supports_speed"): bool,
                    vol.Optional("cover_supports_position"): bool,
                    vol.Optional("media_player_supports_pause"): bool,
                    vol.Optional("media_player_supports_volume_set"): bool,
                    vol.Optional("media_player_supports_next_track"): bool,
                }
            ],
            vol.Optional("floors"): [{vol.Required("name"): vol.Any(str, [str])}],
            vol.Optional("areas"): [{vol.Required("name"): vol.Any(str, [str])}],
        },
    }
)

TEST_SENTENCES_SCHEMA = vol.Schema(
    {
        vol.Required("language"): str,
        vol.Required("sentences"): [str],
        vol.Optional("failing_transcriptions"): [str],
    }
)


def test_validate_shared_lists() -> None:
    """Validate shared lists."""
    with open(SETTINGS.shared_lists_path, "r", encoding="utf-8") as shared_lists_file:
        shared_lists_dict = yaml.load(shared_lists_file)
        validate_with_humanized_errors(shared_lists_dict, SHARED_LISTS_SCHEMA)


@pytest.mark.parametrize("language", TEST_LANGUAGES)
def test_validate_fixtures(language: str) -> None:
    """Test that fixture YAML files match expected schema."""
    lang_test_fixtures_path = TESTS_DIR / "fixtures" / f"{language}.yaml"
    assert (
        lang_test_fixtures_path.exists()
    ), f"Missing test fixtures file for language '{language}' at '{lang_test_fixtures_path}'"

    with open(
        lang_test_fixtures_path, "r", encoding="utf-8"
    ) as lang_test_fixtures_file:
        lang_test_fixtures_dict = yaml.load(lang_test_fixtures_file)
        validate_with_humanized_errors(lang_test_fixtures_dict, FIXTURES_SCHEMA)

    assert lang_test_fixtures_dict.get("language") == language


@pytest.mark.parametrize("language", TEST_LANGUAGES)
def test_validate_test_sentences(language: str) -> None:
    """Test that test sentences YAML files match expected schema."""
    lang_test_sentences_path = TESTS_DIR / "sentences" / f"{language}.yaml"
    assert (
        lang_test_sentences_path.exists()
    ), f"Missing test sentences file for language '{language}' at '{lang_test_sentences_path}'"

    with open(
        lang_test_sentences_path, "r", encoding="utf-8"
    ) as lang_test_sentences_file:
        lang_test_sentences_dict = yaml.load(lang_test_sentences_file)
        validate_with_humanized_errors(lang_test_sentences_dict, TEST_SENTENCES_SCHEMA)

    assert lang_test_sentences_dict.get("language") == language
