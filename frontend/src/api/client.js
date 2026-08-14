import axios from 'axios'

// Set VITE_API_BASE_URL in frontend/.env if your backend isn't on localhost:8000
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // video understanding + LLM calls can take a while
})

export async function fetchLanguages() {
  const { data } = await client.get('/api/languages')
  return data.languages
}

export async function generateNotes(url, language) {
  const { data } = await client.post('/api/notes', { url, language })
  return data
}

export async function downloadNotesPdf(payload) {
  const response = await client.post('/api/pdf', payload, {
    responseType: 'blob',
  })
  return response.data
}

export function extractErrorMessage(error) {
  if (error?.response?.data?.detail) return error.response.data.detail
  if (error?.message) return error.message
  return 'Something went wrong. Please try again.'
}

export default client
