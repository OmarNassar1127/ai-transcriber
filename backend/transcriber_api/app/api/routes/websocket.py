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

                if message.get("type") != "audio":
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unsupported message type: {message.get('type')}"
                    })
                    continue

                # Handle audio message
                if "testPhrase" in message:
                    logger.info(f"Processing test phrase from {username}: {message['testPhrase']}")
                    result = {
                        "type": "transcription",
                        "speaker": username,
                        "text": message["testPhrase"],
                        "timestamp": message.get("timestamp", None)
                    }
                elif "audio" in message:
                    try:
                        # Decode and validate base64 audio data
                        audio_data = base64.b64decode(message["audio"])
                        if not audio_data:
                            raise ValueError("Empty audio data received")
                        result = await audio_processor.process_audio(audio_data, username)
                    except Exception as e:
                        error_msg = f"Audio processing error: {str(e)}"
                        logger.error(error_msg)
                        await websocket.send_json({
                            "type": "error",
                            "message": error_msg
                        })
                        continue
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Message must contain either 'testPhrase' or 'audio' data"
                    })
                    continue

                # Broadcast valid transcription to all connected users
                logger.info(f"Broadcasting transcription result: {result}")
                for user_ws in connected_users.values():
                    await user_ws.send_json(result)

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Server error: {str(e)}"
                })

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        if username in connected_users:
            logger.info(f"Removing disconnected user: {username}")
            del connected_users[username]
