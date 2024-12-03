from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from typing import List, Dict
import json
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pydantic import BaseModel

class TranscriptData(BaseModel):
    transcript: List[Dict]

router = APIRouter()

@router.post("/export/{format}")
async def export_transcript(format: str, data: TranscriptData):
    try:
        transcript = data.transcript
        if format == 'txt':
            # Create text format
            content = '\n'.join([f"{entry['speaker']}: {entry['text']}" for entry in transcript])
            stream = io.StringIO()
            stream.write(content)
            stream.seek(0)

            return StreamingResponse(
                iter([stream.getvalue().encode()]),
                media_type="text/plain",
                headers={"Content-Disposition": f"attachment; filename=transcript.txt"}
            )

        elif format == 'json':
            # Create JSON format
            stream = io.StringIO()
            json.dump(transcript, stream, indent=2)
            stream.seek(0)

            return StreamingResponse(
                iter([stream.getvalue().encode()]),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=transcript.json"}
            )

        elif format == 'pdf':
            # Create PDF format
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            y = 750  # Starting y position

            for entry in transcript:
                if y < 50:  # Check if we need a new page
                    p.showPage()
                    y = 750

                text = f"{entry['speaker']}: {entry['text']}"
                p.drawString(50, y, text)
                y -= 20  # Move down for next line

            p.save()
            buffer.seek(0)

            return StreamingResponse(
                iter([buffer.getvalue()]),
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=transcript.pdf"}
            )

        else:
            raise HTTPException(status_code=400, detail="Unsupported format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
