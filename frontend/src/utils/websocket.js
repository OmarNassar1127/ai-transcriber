export const connectWebSocket = async (userName) => {
  return new Promise((resolve, reject) => {
    try {
      const ws = new WebSocket(`ws://localhost:8000/ws/transcribe/${userName}`);
      let heartbeatInterval;

      ws.onopen = () => {
        console.log('WebSocket connection established');

        // Start heartbeat to keep connection alive
        heartbeatInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'heartbeat' }));
          }
        }, 30000);

        resolve(ws);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        clearInterval(heartbeatInterval);
        reject(new Error('Failed to connect to WebSocket server'));
      };

      ws.onclose = (event) => {
        console.log('WebSocket connection closed:', event.code, event.reason);
        clearInterval(heartbeatInterval);
        if (event.code !== 1000) {
          // Abnormal closure
          console.error('WebSocket closed abnormally. Attempting to reconnect...');
          setTimeout(() => connectWebSocket(userName), 3000);
        }
      };

      // Remove the onmessage handler from here since it's now handled in TranscriptionPanel
      // This allows the component to manage its own state updates
      ws.onmessage = null;

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      reject(error);
    }
  });
};
