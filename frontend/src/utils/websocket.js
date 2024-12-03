export const connectWebSocket = async (userName) => {
  return new Promise((resolve, reject) => {
    try {
      const ws = new WebSocket(`ws://localhost:8000/api/ws/transcribe/${userName}`);
      let heartbeatInterval;
      let reconnectAttempts = 0;
      const MAX_RECONNECT_ATTEMPTS = 5;

      ws.onopen = () => {
        console.log('WebSocket connection established');
        reconnectAttempts = 0;

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

        if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          console.log(`Attempting to reconnect (${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})...`);
          setTimeout(() => {
            reconnectAttempts++;
            connectWebSocket(userName)
              .then(resolve)
              .catch(reject);
          }, Math.min(1000 * Math.pow(2, reconnectAttempts), 30000));
        } else {
          reject(new Error('Failed to connect to WebSocket server after multiple attempts'));
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket connection closed:', event.code, event.reason);
        clearInterval(heartbeatInterval);

        if (event.code !== 1000 && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
          console.log(`Connection closed abnormally. Attempting to reconnect (${reconnectAttempts + 1}/${MAX_RECONNECT_ATTEMPTS})...`);
          setTimeout(() => {
            reconnectAttempts++;
            connectWebSocket(userName)
              .then(resolve)
              .catch(reject);
          }, Math.min(1000 * Math.pow(2, reconnectAttempts), 30000));
        }
      };

      // Remove the onmessage handler since it's handled in TranscriptionPanel
      ws.onmessage = null;

    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      reject(error);
    }
  });
};
