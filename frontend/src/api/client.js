import axios from 'axios'

// In production (npm run build), this app is served BY the FastAPI backend
// itself, so requests can stay relative ('') — same origin, no CORS.
//
// In dev (npm run dev, hot-reload on :5173) it defaults to localhost:8000.
// Override either with VITE_API_BASE_URL in frontend/.env if your backend
// runs somewhere else.
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? 'http://localhost:8000' : '')

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
