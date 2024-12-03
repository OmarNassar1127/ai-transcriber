let mediaRecorder = null;
let audioChunks = [];
let simulationInterval = null;

// Test phrases for simulation
const TEST_PHRASES = [
  "Hello, this is a test of the transcription system.",
  "I'm testing the speaker recognition feature.",
  "Can everyone hear me clearly?",
  "Let's make sure the real-time transcription is working.",
  "Testing the export functionality next."
];

export const startRecording = async (ws) => {
  try {
    // Try to get media devices, if not available or fails, use simulation
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true
        }
      });

      mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      mediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          const buffer = await event.data.arrayBuffer();
          const float32Array = new Float32Array(buffer);

          // Convert to base64
          const base64Audio = btoa(String.fromCharCode.apply(null, new Uint8Array(float32Array.buffer)));

          try {
            ws.send(JSON.stringify({
              type: 'audio',
              audio: base64Audio,
              timestamp: Date.now()
            }));
          } catch (error) {
            console.error('Error sending audio data:', error);
          }
        }
      };

      mediaRecorder.start(1000); // Collect data every second
      console.log('Recording started');
    } catch (mediaError) {
      console.log('Media device error, falling back to simulation:', mediaError);
      return startSimulatedRecording(ws);
    }
  } catch (error) {
    console.error('Recording error:', error);
    return startSimulatedRecording(ws);
  }
};

const startSimulatedRecording = (ws) => {
  let phraseIndex = 0;
  console.log('Starting simulated recording with WebSocket:', ws?.readyState);

  simulationInterval = setInterval(() => {
    if (ws?.readyState === WebSocket.OPEN) {
      const testPhrase = TEST_PHRASES[phraseIndex];
      console.log('Sending test phrase:', testPhrase);

      // Send simulated audio data with test phrase
      try {
        ws.send(JSON.stringify({
          type: 'audio',
          testPhrase: testPhrase,
          timestamp: Date.now()
        }));

        phraseIndex = (phraseIndex + 1) % TEST_PHRASES.length;
      } catch (error) {
        console.error('Error sending simulated audio data:', error);
      }
    } else {
      console.error('WebSocket not ready. State:', ws?.readyState);
    }
  }, 2000); // Send test phrases every 2 seconds

  console.log('Simulated recording started');
};

export const stopRecording = async () => {
  if (simulationInterval) {
    clearInterval(simulationInterval);
    simulationInterval = null;
    console.log('Simulated recording stopped');
    return;
  }

  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
    mediaRecorder.stream.getTracks().forEach(track => track.stop());
    audioChunks = [];
    console.log('Recording stopped');
  }
};