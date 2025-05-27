import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { initializeApi } from './api/apiConfig'

// Initialize the API client with the backend URL
// No authentication tokens will be set for development
initializeApi({
  baseUrl: 'http://localhost:8002/api/v1',
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
