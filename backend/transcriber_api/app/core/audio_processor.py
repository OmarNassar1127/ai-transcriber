import whisper
import numpy as np
from typing import Dict
from app.core.config import settings

class AudioProcessor:
    def __init__(self):
        self.model = whisper.load_model("base")

    async def process_audio(self, audio_data: bytes) -> dict:
        """Process audio data using local Whisper model"""
        try:
            # Preprocess audio data
            processed_audio = self.preprocess_audio(audio_data)

            # Run inference with Whisper
            result = self.model.transcribe(processed_audio)

            return {
                "text": result["text"],
                "segments": result.get("segments", []),
                "language": result.get("language", "en")
            }
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            return {"error": str(e)}

    @staticmethod
    def preprocess_audio(audio_data: bytes) -> np.ndarray:
        """Preprocess audio data for Whisper"""
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.float32)

            # Normalize audio (if needed)
            if np.abs(audio_array).max() > 1.0:
                audio_array = audio_array / np.abs(audio_array).max()

            return audio_array
        except Exception as e:
            print(f"Error preprocessing audio: {str(e)}")
            raise e

audio_processor = AudioProcessor()
