# AI Transcriber

Real-time meeting transcription application with speaker recognition using Whisper AI.

## Features
- Voice Recognition with speaker identification
- Real-time transcription
- Speaker registration system
- Multiple export formats (Text, PDF, JSON)
- Modern React.js frontend
- FastAPI backend for audio processing

## Local Development Setup

### Prerequisites
- Node.js (v16 or higher)
- Python 3.12
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/OmarNassar1127/ai-transcriber.git
cd ai-transcriber
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

3. Install backend dependencies:
```bash
cd backend/transcriber_api
pip install -r requirements.txt
cd ../..
```

### Running the Application

Start the backend server:
```bash
cd backend/transcriber_api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

In a new terminal, start the frontend:
```bash
cd frontend
npm start
```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Project Structure
```
ai-transcriber/
├── frontend/                # React.js frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── utils/          # Utility functions
│   │   └── App.js
│   └── package.json
└── backend/
    └── transcriber_api/
        ├── app/
        │   ├── api/        # API routes
        │   ├── core/       # Core functionality
        │   └── models/     # Data models
        └── requirements.txt
```
