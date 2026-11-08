# syntax=docker/dockerfile:1

FROM debian:bookworm-slim

ARG TARGETARCH
ARG TARGETVARIANT

WORKDIR /usr/src

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libencode-perl \
        libopenblas0 \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
    && mkdir ./tools \
    && curl --fail --location \
        "https://huggingface.co/datasets/rhasspy/rhasspy-speech/resolve/main/tools/rhasspy-speech_${TARGETARCH}${TARGETVARIANT}.tar.gz?download=true" \
        | tar -C ./tools -xzf - \
    && python3 -m venv .venv

COPY pyproject.toml ./
COPY speech_to_phrase/ ./speech_to_phrase/
RUN .venv/bin/pip install --no-cache-dir . \
    && apt-get remove --yes build-essential curl python3-dev python3-pip \
    && apt-get autoremove --yes \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY run.sh ./run.sh

WORKDIR /

EXPOSE 10300

ENTRYPOINT ["bash", "/usr/src/run.sh"]
