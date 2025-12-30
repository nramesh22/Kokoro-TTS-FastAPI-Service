from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from kokoro import KPipeline
import soundfile as sf
import uuid
import os

# Initialize FastAPI
app = FastAPI(title="Kokoro TTS API")

# Initialize Kokoro pipeline once (important for performance)
pipeline = KPipeline(lang_code="a")  # default language code

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class TTSRequest(BaseModel):
    text: str
    voice: str = "af_heart"
    sample_rate: int = 24000
    speed: float = 0.50  # 0.25–1.0 recommended


@app.post("/tts")
def text_to_speech(request: TTSRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Best voices for affirmations
    # For English affirmations, these voices are generally the most suitable choices.​
    # af_heart (US female, high‑quality; emoji 🚺❤️ suggests a gentle, emotional timbre)
    # af_bella (US female, high target quality, long training “HH hours”)
    # af_nicole (US female, studio/🎧 style; balanced and clear)
    # af_sarah (US female, good training duration, neutral/soft)
    # bf_emma (UK female, strong training “HH hours”, natural British tone)
    # bf_isabella (UK female, default female voice in some integrations)
    # am_michael / am_fenrir (US male, decent quality, work well for calm but confident male affirmations)
    # bm_george / bm_fable (UK male, good for reassuring, articulate British male reads)

    if not (0.25 <= request.speed <= 1.0):
        raise HTTPException(
            status_code=400,
            detail="Speed must be between 0.25 and 1.0"
        )

    generator = pipeline(
        request.text,
        voice=request.voice,
        speed=request.speed
    )

    # Kokoro can generate multiple audio chunks
    output_files = []

    for i, (_, _, audio) in enumerate(generator):
        filename = f"{uuid.uuid4()}_{i}.wav"
        filepath = os.path.join(OUTPUT_DIR, filename)

        sf.write(filepath, audio, request.sample_rate)
        output_files.append(filepath)

    # If only one chunk, return it directly
    if len(output_files) == 1:
        return FileResponse(
            output_files[0],
            media_type="audio/wav",
            filename="speech.wav",
        )

    # If multiple chunks, return the first (or you can zip them)
    return FileResponse(
        output_files[0],
        media_type="audio/wav",
        filename="speech_part_0.wav",
    )
