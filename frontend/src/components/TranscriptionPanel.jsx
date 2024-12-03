import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Container,
  Heading,
  Text,
  VStack,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Input,
  List,
  ListItem
} from '@chakra-ui/react';
import { startRecording, stopRecording } from '../utils/audioRecorder';
import { connectWebSocket } from '../utils/websocket';

const TranscriptionPanel = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState([]);
  const [isNameModalOpen, setIsNameModalOpen] = useState(true);
  const [userName, setUserName] = useState('');
  const [webSocket, setWebSocket] = useState(null);
  const toast = useToast();

  useEffect(() => {
    return () => {
      if (webSocket) {
        webSocket.close();
      }
    };
  }, [webSocket]);

  const handleStartRecording = async () => {
    try {
      let ws = webSocket;
      // Ensure WebSocket is connected before starting recording
      if (!ws) {
        ws = await connectWebSocket(userName);

        // Set up WebSocket handlers before using it
        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log('Received WebSocket message:', data);

            switch (data.type) {
              case 'transcription':
                if (data.text) {
                  setTranscript(prev => [...prev, {
                    speaker: data.speaker || userName,
                    text: data.text,
                    timestamp: data.timestamp
                  }]);
                }
                break;
              case 'registration':
                toast({
                  title: 'Connected',
                  description: `Registered as ${data.name}`,
                  status: 'success',
                  duration: 2000,
                });
                break;
              case 'error':
                console.error('Server error:', data.message);
                toast({
                  title: 'Error',
                  description: data.message,
                  status: 'error',
                  duration: 3000,
                });
                break;
              case 'heartbeat':
                // Silently handle heartbeat responses
                break;
              default:
                console.log('Received unknown message type:', data);
            }
          } catch (error) {
            console.error('Error processing message:', error);
            toast({
              title: 'Error',
              description: 'Failed to process server message',
              status: 'error',
              duration: 3000,
            });
          }
        };

        setWebSocket(ws);
      }

      // Start recording only after WebSocket is confirmed ready
      await startRecording(ws); // Pass the WebSocket instance directly
      setIsRecording(true);
      toast({
        title: 'Recording started',
        description: 'Using simulated audio for testing',
        status: 'success',
        duration: 2000,
      });
    } catch (error) {
      console.error('Recording error:', error);
      toast({
        title: 'Error starting recording',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleStopRecording = async () => {
    try {
      await stopRecording();
      setIsRecording(false);
      toast({
        title: 'Recording stopped',
        status: 'info',
        duration: 2000,
      });
    } catch (error) {
      toast({
        title: 'Error stopping recording',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleExport = async (format) => {
    try {
      const response = await fetch(`http://localhost:8001/api/export/${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ transcript }),
      });

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `transcript.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast({
        title: 'Export successful',
        status: 'success',
        duration: 2000,
      });
    } catch (error) {
      toast({
        title: 'Export failed',
        description: error.message,
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleNameSubmit = () => {
    if (userName.trim()) {
      setIsNameModalOpen(false);
    } else {
      toast({
        title: 'Please enter your name',
        status: 'warning',
        duration: 2000,
      });
    }
  };

  return (
    <Container maxW="container.xl" py={8}>
      <Modal isOpen={isNameModalOpen} onClose={() => {}} closeOnOverlayClick={false}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Enter Your Name</ModalHeader>
          <ModalBody pb={6}>
            <Input
              placeholder="Your name"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleNameSubmit()}
            />
            <Button mt={4} colorScheme="blue" onClick={handleNameSubmit}>
              Start
            </Button>
          </ModalBody>
        </ModalContent>
      </Modal>

      <VStack spacing={6} align="stretch">
        <Heading>AI Meeting Transcriber</Heading>

        <Box>
          <Button
            colorScheme={isRecording ? 'red' : 'green'}
            onClick={isRecording ? handleStopRecording : handleStartRecording}
            mr={4}
          >
            {isRecording ? 'Stop Recording' : 'Start Recording'}
          </Button>

          <Button
            colorScheme="blue"
            onClick={() => handleExport('txt')}
            mr={2}
            isDisabled={transcript.length === 0}
          >
            Export TXT
          </Button>
          <Button
            colorScheme="blue"
            onClick={() => handleExport('json')}
            mr={2}
            isDisabled={transcript.length === 0}
          >
            Export JSON
          </Button>
          <Button
            colorScheme="blue"
            onClick={() => handleExport('pdf')}
            isDisabled={transcript.length === 0}
          >
            Export PDF
          </Button>
        </Box>

        <Box borderWidth={1} borderRadius="lg" p={4} minH="400px" maxH="600px" overflowY="auto">
          <List spacing={3}>
            {transcript.map((entry, index) => (
              <ListItem key={index}>
                <Text>
                  <strong>{entry.speaker}:</strong> {entry.text}
                </Text>
              </ListItem>
            ))}
          </List>
          {/* Debug Panel */}
          <Box mt={4} p={2} bg="gray.100" borderRadius="md">
            <Text fontSize="sm" color="gray.600">Debug Info:</Text>
            <Text fontSize="sm">WebSocket Status: {webSocket ? 'Connected' : 'Disconnected'}</Text>
            <Text fontSize="sm">Recording Status: {isRecording ? 'Active' : 'Inactive'}</Text>
            <Text fontSize="sm">Current User: {userName}</Text>
            <Text fontSize="sm">Transcript Length: {transcript.length}</Text>
          </Box>
        </Box>
      </VStack>
    </Container>
  );
};

export default TranscriptionPanel;
