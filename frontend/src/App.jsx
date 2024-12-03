import { ChakraProvider } from '@chakra-ui/react'
import TranscriptionPanel from './components/TranscriptionPanel'

function App() {
  return (
    <ChakraProvider>
      <TranscriptionPanel />
    </ChakraProvider>
  )
}

export default App
