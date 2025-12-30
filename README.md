# Kokoro TTS FastAPI Service

A lightweight **Text-to-Speech (TTS) REST API** built with **FastAPI** and **Kokoro-82M**, optimized for low-latency speech synthesis and suitable for affirmation, narration, and conversational use cases.

---

## Features

- FastAPI-based REST endpoint
- High-quality Kokoro voices (US & UK, male & female)
- Chunk-based audio generation support
- WAV audio output (24 kHz default)
- Single pipeline initialization for optimal performance
- Simple JSON request/response model

---

## Architecture Overview

Client (Next.js / cURL / App)
|
v
FastAPI (/tts endpoint)
|
v
Kokoro KPipeline (initialized once)
|
v
Audio Chunks (NumPy arrays)
|
v
WAV Output (soundfile)


---

## Supported Voices

**US Female**
- `af_heart` – soft, emotional, calming (recommended default)
- `af_bella` – high-quality, long-trained
- `af_nicole` – studio-style, balanced
- `af_sarah` – neutral and soothing

**UK Female**
- `bf_emma`
- `bf_isabella`

**US Male**
- `am_michael`
- `am_fenrir`

**UK Male**
- `bm_george`
- `bm_fable`

---

## Installation

### 1. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate

### 2. Install Dependencies

pip install -r requirements.txt

Running the API

uvicorn main:app --host 0.0.0.0 --port 8880

### Directory Structure

.
├── main.py
├── requirements.txt
├── README.md
└── outputs/
    └── *.wav

### Endpoint

POST /tts


### Request Body

{
  "text": "I am calm, confident, and focused.",
  "voice": "af_heart",
  "speed": 0.5,
  "sample_rate": 24000
}


### Speech Speed Control

The `speed` parameter controls how fast the speech is generated.

| Speed Value | Description |
|------------|------------|
| 0.25       | Very slow, meditative |
| 0.40–0.60  | Calm affirmations (recommended) |
| 0.75       | Natural conversational pace |
| 1.0        | Fast speech |

**Recommended for affirmations:** `0.45 – 0.60`

### Example cURL (Updated)

curl -X POST http://localhost:8880/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I am grounded and at peace.",
    "voice": "af_heart",
    "speed": 0.45
  }' \
  --output affirmation.wav

