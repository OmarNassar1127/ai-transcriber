from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Speaker(BaseModel):
    id: str
    name: str

class TranscriptionSegment(BaseModel):
    speaker_id: str
    text: str
    timestamp: datetime

class Transcription(BaseModel):
    id: str
    speakers: List[Speaker]
    segments: List[TranscriptionSegment]
    created_at: datetime
    updated_at: datetime
