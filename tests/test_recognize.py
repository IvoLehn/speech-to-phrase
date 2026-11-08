"""Test that configured sentence templates are used for recognition."""

from pathlib import Path

from hassil import recognize_all

from speech_to_phrase import Settings
from speech_to_phrase.hass_api import Things
from speech_to_phrase.models import MODELS
from speech_to_phrase.train import _create_intents

from . import LOCAL_DIR, SETTINGS, TESTS_DIR


def test_recognize_configured_templates_only(tmp_path: Path) -> None:
    """Load templates from the configured directory without bundled defaults."""
    settings = Settings(
        models_dir=SETTINGS.models_dir,
        train_dir=tmp_path,
        tools_dir=LOCAL_DIR,
        templates_dirs=[TESTS_DIR / "templates"],
        hass_token="",
        hass_websocket_uri="",
        retrain_on_connect=False,
    )
    settings.model_train_dir(MODELS["en"].id).mkdir(parents=True)

    intents = _create_intents(MODELS["en"], settings, Things())

    assert set(intents.intents) == {"HassSetTemperature"}
    result = next(iter(recognize_all("set temperature to 22 degrees", intents)), None)

    assert result is not None
    assert result.intent.name == "HassSetTemperature"
