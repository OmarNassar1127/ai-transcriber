from typing import Dict, List, Optional
import uuid

class Speaker:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name

class SpeakerManager:
    def __init__(self):
        self.speakers: Dict[str, Speaker] = {}
        self.active_connections: Dict[str, str] = {}  # WebSocket ID to Speaker ID mapping

    def register_speaker(self, name: str) -> Speaker:
        speaker = Speaker(name)
        self.speakers[speaker.id] = speaker
        return speaker

    def get_speaker(self, speaker_id: str) -> Optional[Speaker]:
        return self.speakers.get(speaker_id)

    def associate_connection(self, connection_id: str, speaker_id: str):
        self.active_connections[connection_id] = speaker_id

    def get_speaker_by_connection(self, connection_id: str) -> Optional[Speaker]:
        speaker_id = self.active_connections.get(connection_id)
        if speaker_id:
            return self.get_speaker(speaker_id)
        return None

speaker_manager = SpeakerManager()
