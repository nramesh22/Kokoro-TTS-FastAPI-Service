from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from kokoro import KPipeline
import soundfile as sf
import uuid
import os
import numpy as np

# Initialize FastAPI
app = FastAPI(title="Kokoro TTS API")

# Initialize Kokoro pipeline once
pipeline = KPipeline(lang_code="a")

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLE_RATE = 24000  # Kokoro native sample rate


class TTSRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    speed: float = 0.65  # Stable sweet spot for affirmations


@app.post("/tts")
def text_to_speech(request: TTSRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if not (0.5 <= request.speed <= 1.0):
        raise HTTPException(
            status_code=400,
            detail="Speed must be between 0.5 and 1.0"
        )

    generator = pipeline(
        request.text,
        voice=request.voice,
        speed=request.speed
    )

    audio_chunks = []

    for i, (_, _, audio) in enumerate(generator):
        audio_arr = to_ndarray(audio)
        if audio_arr.size == 0:
            continue
        if i == 0:
            audio_arr = trim_leading_silence(audio_arr)
        if audio_arr.size > 0:
            audio_chunks.append(audio_arr)

    if not audio_chunks:
        raise HTTPException(status_code=500, detail="No audio produced for the requested text")

    final_audio = np.concatenate(audio_chunks)

    # Remove breath/noise safely
    final_audio = trim_leading_silence(final_audio)

    # Gentle studio fade-in
    final_audio = fade_in(final_audio, SAMPLE_RATE, fade_ms=12)

    # Smooth studio fade-in
    final_audio = fade_in(final_audio, SAMPLE_RATE, fade_ms=15)

    filename = f"{uuid.uuid4()}.wav"
    filepath = os.path.join(OUTPUT_DIR, filename)

    # Write using Kokoro's native sample rate
    sf.write(filepath, final_audio, SAMPLE_RATE)

    return FileResponse(
        filepath,
        media_type="audio/wav",
        filename="speech.wav"
    )

def trim_leading_silence(audio, threshold=1e-4, backtrack=10):
    if audio.size == 0:
        return audio
    non_silent = np.flatnonzero(np.abs(audio) > threshold)
    if non_silent.size == 0:
        return audio
    start = max(int(non_silent[0]) - backtrack, 0)
    return audio[start:]

def hard_trim_start(audio, sample_rate, trim_ms=180):
    trim_samples = int(sample_rate * trim_ms / 1000)
    return audio[trim_samples:]

def fade_in(audio, sample_rate, fade_ms=15):
    audio = to_ndarray(audio)
    fade_samples = int(sample_rate * fade_ms / 1000)
    fade_curve = np.linspace(0, 1, fade_samples)
    audio[:fade_samples] *= fade_curve
    return audio

def to_ndarray(audio):
    # Normalize various tensor/array types to numpy for size/ops safety
    return np.asarray(audio)