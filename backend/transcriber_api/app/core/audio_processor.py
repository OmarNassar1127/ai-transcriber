import whisper
import numpy as np
import base64
from typing import Dict
from app.core.config import settings

class AudioProcessor:
    def __init__(self):
        self.model = whisper.load_model("base")

    async def process_audio(self, audio_data: str) -> dict:
        """Process audio data using local Whisper model"""
        try:
            # Decode base64 audio data and preprocess
            decoded_audio = base64.b64decode(audio_data)
            processed_audio = self.preprocess_audio(decoded_audio)

            # Run inference with Whisper
            result = self.model.transcribe(processed_audio)

            return {
                "type": "transcription",
                "text": result["text"],
                "segments": result.get("segments", []),
                "language": result.get("language", "en")
            }
        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            return {"type": "error", "message": str(e)}

    @staticmethod
    def preprocess_audio(audio_data: bytes) -> np.ndarray:
        """Preprocess PCM16 audio data for Whisper"""
        try:
            # Convert bytes to Int16 numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)

            # Convert to float32 and normalize to [-1, 1]
            audio_array = audio_array.astype(np.float32) / 32768.0

            return audio_array
        except Exception as e:
            print(f"Error preprocessing audio: {str(e)}")
            raise e

audio_processor = AudioProcessor()
