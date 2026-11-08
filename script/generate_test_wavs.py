"""Generate test WAV files using Home Assistant."""

import argparse
import json
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from ruamel.yaml import YAML

_DIR = Path(__file__).parent
_REPO_DIR = _DIR.parent
_TESTS_DIR = _REPO_DIR / "tests"
_TEST_SENTENCES_DIR = _TESTS_DIR / "sentences"
_BACKGROUND_NOISE_WAV = _TESTS_DIR / "wav" / "background_noise.wav"

_LOGGER = logging.getLogger(__name__)

TTS_LANG = {
    "en": "en-US",
    "el": "el-GR",
    "cs": "cs-CZ",
    "ca": "ca-ES",
    "pt_PT": "pt-PT",
    "hi": "hi-IN",
    "eu": "eu-ES",
    "fa": "fa-IR",
    "sl": "sl-SI",
    "sw": "sw-KE",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hass-url", default="http://localhost:8123")
    parser.add_argument("--hass-token", required=True)
    parser.add_argument("--engine", default="tts.home_assistant_cloud")
    parser.add_argument(
        "--output-dir", default=_TESTS_DIR / "wav", help="Path to output directory"
    )
    parser.add_argument("--language", help="Only generate WAV files for language")
    parser.add_argument(
        "--delete", action="store_true", help="Delete unneeded WAV files"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    output_dir = Path(args.output_dir)

    if not shutil.which("sox"):
        _LOGGER.fatal("sox must be installed")
        return 1

    yaml = YAML(typ="safe")
    for test_sentences_path in sorted(_TEST_SENTENCES_DIR.glob("*.yaml")):
        language = test_sentences_path.stem

        if args.language and (language != args.language):
            continue

        tts_language = TTS_LANG.get(language, f"{language}-{language.upper()}")

        lang_wav_dir = output_dir / language
        lang_gen_wav_dir = lang_wav_dir / "generated"
        lang_gen_wav_dir.mkdir(parents=True, exist_ok=True)

        # Load test sentences
        with open(test_sentences_path, "r", encoding="utf-8") as test_sentences_file:
            test_sentences_dict = yaml.load(test_sentences_file)

        test_sentences = test_sentences_dict["sentences"]

        generated_wav_names: set[str] = set()
        for sentence in test_sentences:
            wav_path = lang_wav_dir / f"{sentence}.wav"
            gen_wav_path = lang_gen_wav_dir / f"{sentence}.wav"
            generated_wav_names.add(sentence)

            if wav_path.exists() or gen_wav_path.exists():
                continue

            generate_wav(
                args.hass_url,
                args.hass_token,
                args.engine,
                tts_language,
                sentence,
                gen_wav_path,
            )
            print(wav_path)

        if args.delete:
            for gen_wav_path in lang_gen_wav_dir.glob("*.wav"):
                if gen_wav_path.stem in generated_wav_names:
                    continue

                gen_wav_path.unlink()
                print("DELETED:", gen_wav_path)

    return 0


# -----------------------------------------------------------------------------


def generate_wav(
    hass_url: str,
    hass_token: str,
    engine: str,
    language: str,
    text: str,
    wav_path: Path,
) -> None:
    request = Request(
        f"{hass_url}/api/tts_get_url",
        data=json.dumps(
            {"engine_id": engine, "message": text, "language": language}
        ).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {hass_token}",
        },
    )
    with urlopen(request) as response:
        audio_url = json.load(response)["url"]

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)

        wav_no_noise = temp_dir / "no_noise.wav"
        wav_bg_noise = temp_dir / "bg_noise.wav"

        with urlopen(audio_url) as response:
            subprocess.check_call(
                [
                    "sox",
                    "-t",
                    "mp3",
                    "-",
                    "-r",
                    "16000",
                    "-c",
                    "1",
                    "-e",
                    "signed-integer",
                    "-b",
                    "16",
                    "-t",
                    "wav",
                    str(wav_no_noise),
                    "lowpass",
                    "5000",
                    "highpass",
                    "200",
                    "reverb",
                    "50",
                    "50",
                    "100",
                    "pad",
                    "0.2",
                ],
                stdin=response,
            )

        wav_duration = (
            subprocess.check_output(["soxi", "-D", str(wav_no_noise)]).decode().strip()
        )

        # Add background noise
        subprocess.check_call(
            [
                "sox",
                str(_BACKGROUND_NOISE_WAV),
                str(wav_bg_noise),
                "vol",
                "2",
                "trim",
                "0",
                wav_duration,
            ]
        )
        subprocess.check_call(
            [
                "sox",
                "-m",
                str(wav_bg_noise),
                str(wav_no_noise),
                "-b",
                "16",
                str(wav_path),
            ]
        )


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    main()
