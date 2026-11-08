# Contributing

Contributions to Speech-to-Phrase are welcome! There are two parts that are required for a language to be supported:

1. A [speech-to-text model](#speech-to-text-models)
2. A set of [sentence templates](#snetence-templates)

Not all speech-to-text models and sentence templates are usable in Speech-to-Phrase. All models must be able to run quickly on a Raspberry Pi 4 (less than 1 second of processing time), and all sentences must be [recognized by Home Assistant](https://github.com/home-assistant/intents/).


## Speech-to-Text Models

There are currently two types of supported speech-to-text models:

* [Kaldi][kaldi]
* [Coqui STT][coqui-stt]

Pre-packaged models are available to [download from HuggingFace][model-download].

### Kaldi

These are [nnet3][] models that also have a [Phonetisaurus][] grapheme-to-phoneme (g2p) model for guessing word pronunciations. 

Some of the models were trained with [ipa2kaldi][]. See the [English model][english-model] for an example.

### Coqui STT

These models were [downloaded from GitHub][coqui-models] and repackaged for Speech-to-Phrase. Fortunately, the scorers are not needed because we only use the raw probabilities from the Coqui STT model. The language model probabilities are generated during Speech-to-Phrase's training.

<!----------------------------------------------------------------------------->

## Sentence Templates

Speech-to-Phrase trains itself based on Home Assistant's [exposed][]:

* [entities][]
* [areas][area]
* [floors][floor]

Sentence templates are supplied by the user and must use phrases recognizable by [Home Assistant][intents].

Sentence templates use Home Assistant's [sentence YAML format][hassil-syntax] and are provided at runtime through `--templates-dir`. Each language has a subdirectory containing one or more YAML files. Test templates live in `tests/templates`.

The speech-to-text models perform best with a manageable set of possible sentences, so keep templates concise.

### Tests

To test transcriptions, a fixtures file must be added at `tests/fixtures/<language>.yaml` with:

```yaml
language: "<language code>"

fixtures:
  floors:
    - name: "Floor name"
    - name: "..."

  areas:
    - name: "Area name"
    - name: "..."

  entities:
    - name: "Entity name"
      domain: "entity_domain"

    - name: "..."
      domain: "..."
```

Supported features can also be added to entities:

```yaml
fixtures:
  entities:
    - name: "Bed Light"
      domain: "light"
      light_supports_brightness: true
      light_supports_color: true
```


<!-- Links -->
[entities]: https://www.home-assistant.io/docs/configuration/entities_domains/
[area]: https://www.home-assistant.io/docs/organizing/#area
[floor]: https://www.home-assistant.io/docs/organizing/#floor
[exposed]: https://www.home-assistant.io/voice_control/voice_remote_expose_devices/
[intents]: https://github.com/home-assistant/intents
[language-leaders]: https://developers.home-assistant.io/docs/voice/language-leaders/
[kaldi]: https://kaldi-asr.org/
[coqui-stt]: https://stt.readthedocs.io/en/latest/
[nnet3]: https://kaldi-asr.org/doc/dnn3.html
[phonetisaurus]: https://github.com/AdolfVonKleist/Phonetisaurus
[model-download]: https://huggingface.co/datasets/rhasspy/rhasspy-speech/tree/main/models
[english-model]: https://huggingface.co/datasets/rhasspy/rhasspy-speech/resolve/main/models/en_US-rhasspy.tar.gz?download=true
[ipa2kaldi]: https://github.com/rhasspy/ipa2kaldi
[coqui-models]: https://github.com/coqui-ai/STT-models
[hassil]: https://github.com/home-assistant/hassil
[hassil-syntax]: https://github.com/home-assistant/hassil?tab=readme-ov-file#sentence-templates
