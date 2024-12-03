import json
from datetime import datetime
from typing import List, Dict
import base64
from fpdf import FPDF

class TranscriptExporter:
    @staticmethod
    def to_json(transcript_data: Dict) -> str:
        """Export transcript to JSON format"""
        return json.dumps({
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "format": "json"
            },
            "transcript": transcript_data
        }, indent=2)

    @staticmethod
    def to_text(transcript_data: Dict) -> str:
        """Export transcript to plain text format"""
        text_output = []
        text_output.append("Meeting Transcript")
        text_output.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        for segment in transcript_data.get("segments", []):
            speaker = segment.get("speaker", "Unknown")
            text = segment.get("text", "")
            timestamp = segment.get("timestamp", "")
            text_output.append(f"[{timestamp}] {speaker}: {text}")

        return "\n".join(text_output)

    @staticmethod
    def to_pdf(transcript_data: Dict) -> bytes:
        """Export transcript to PDF format"""
        pdf = FPDF()
        pdf.add_page()

        # Add title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Meeting Transcript", ln=True, align="C")
        pdf.ln(10)

        # Add metadata
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.ln(10)

        # Add transcript content
        pdf.set_font("Arial", "", 12)
        for segment in transcript_data.get("segments", []):
            speaker = segment.get("speaker", "Unknown")
            text = segment.get("text", "")
            timestamp = segment.get("timestamp", "")

            pdf.multi_cell(0, 10, f"[{timestamp}] {speaker}: {text}")
            pdf.ln(5)

        return pdf.output(dest='S').encode('latin-1')

transcript_exporter = TranscriptExporter()
