from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Optional
from app.core.audio_processor import audio_processor
from app.core.speaker_manager import speaker_manager
from app.utils.export import transcript_exporter
from fastapi.responses import Response
import json
import uuid
from datetime import datetime

router = APIRouter()

# Store active WebSocket connections
connections: Dict[str, WebSocket] = {}

@router.websocket("/ws/transcribe/{speaker_name}")
async def transcribe_audio(websocket: WebSocket, speaker_name: str):
    connection_id = str(uuid.uuid4())
    try:
        await websocket.accept()

        # Register speaker
        speaker = speaker_manager.register_speaker(speaker_name)
        speaker_manager.associate_connection(connection_id, speaker.id)
        connections[connection_id] = websocket

        # Send confirmation
        await websocket.send_json({
            "type": "registration",
            "status": "success",
            "speaker_id": speaker.id,
            "name": speaker_name
        })

        while True:
            # Receive message
            try:
                message = await websocket.receive_text()
                data = json.loads(message)

                if data.get("type") == "audio":
                    # For testing, use the test phrase directly
                    test_phrase = data.get("testPhrase")
                    if test_phrase:
                        # Send transcription back to client
                        await websocket.send_json({
                            "type": "transcription",
                            "text": test_phrase,
                            "speaker": speaker_name,
                            "speaker_id": speaker.id,
                            "timestamp": data.get("timestamp")
                        })
                    else:
                        # Handle real audio data here when implemented
                        await websocket.send_json({
                            "type": "error",
                            "message": "No test phrase provided"
                        })
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON message"
                })

    except WebSocketDisconnect:
        if connection_id in connections:
            del connections[connection_id]
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        if connection_id in connections:
            del connections[connection_id]

@router.get("/speakers")
async def get_speakers():
    return {
        "speakers": [
            {"id": s.id, "name": s.name}
            for s in speaker_manager.speakers.values()
        ]
    }

@router.post("/export/{format}")
async def export_transcript(format: str, transcript_data: Dict):
    """Export transcript in specified format"""
    try:
        if format == "json":
            content = transcript_exporter.to_json(transcript_data)
            return Response(content=content, media_type="application/json")
        elif format == "text":
            content = transcript_exporter.to_text(transcript_data)
            return Response(content=content, media_type="text/plain")
        elif format == "pdf":
            content = transcript_exporter.to_pdf(transcript_data)
            return Response(content=content, media_type="application/pdf")
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-transcript")
async def save_transcript(transcript_data: Dict):
    """Save transcript data"""
    try:
        # Add metadata
        transcript_data["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "total_speakers": len(speaker_manager.speakers)
        }
        return {"status": "success", "transcript": transcript_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
