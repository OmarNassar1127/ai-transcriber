from fastapi import WebSocket
from typing import Dict
import json
import base64
import logging
from app.core.audio_processor import audio_processor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

connected_users: Dict[str, WebSocket] = {}

async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()
    connected_users[username] = websocket
    logger.info(f"New WebSocket connection accepted for user: {username}")

    # Send initial connection confirmation
    await websocket.send_json({
        "type": "connection_status",
        "status": "connected",
        "message": f"User {username} connected successfully"
    })
    logger.info(f"Sent connection confirmation to user: {username}")

    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                logger.info(f"Received message from {username}: {message.get('type')}")

                if message.get("type") == "heartbeat":
                    await websocket.send_json({
                        "type": "heartbeat",
                        "status": "alive"
                    })
                elif message.get("type") == "audio":
                    # For testing: if test phrase is provided, use it directly
                    if "testPhrase" in message:
                        logger.info(f"Processing test phrase from {username}: {message['testPhrase']}")
                        result = {
                            "type": "transcription",
                            "speaker": username,
                            "text": message["testPhrase"],
                            "timestamp": message.get("timestamp", None)
                        }
                    else:
                        # Decode base64 audio data and process with speaker recognition
                        audio_data = base64.b64decode(message["audio"])
                        result = await audio_processor.process_audio(audio_data, username)

                    logger.info(f"Broadcasting transcription result: {result}")
                    # Broadcast transcription to all connected users
                    for user_ws in connected_users.values():
                        await user_ws.send_json(result)

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json({"type": "error", "message": str(e)})

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        if username in connected_users:
            logger.info(f"Removing disconnected user: {username}")
            del connected_users[username]
