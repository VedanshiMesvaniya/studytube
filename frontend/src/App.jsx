import { useEffect, useState } from 'react'
import ThemeToggle from './components/ThemeToggle'
import Hero from './components/Hero'
import SearchForm from './components/SearchForm'
import ResultsPanel from './components/ResultsPanel'
import { fetchLanguages, generateNotes, extractErrorMessage } from './api/client'
import './styles/App.css'

const THEME_KEY = 'studytube-theme'

export default function App() {
  const [theme, setTheme] = useState(
    () => localStorage.getItem(THEME_KEY) || 'academic-dark'
  )
  const [languages, setLanguages] = useState(['Auto Detect', 'English'])
  const [url, setUrl] = useState('')
  const [language, setLanguage] = useState('Auto Detect')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [statusMessage, setStatusMessage] = useState('')
  const [results, setResults] = useState(null)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem(THEME_KEY, theme)
  }, [theme])

  useEffect(() => {
    fetchLanguages()
      .then(setLanguages)
      .catch(() => {
        // Backend not reachable yet — keep the default list so the form still works.
      })
  }, [])

  function toggleTheme() {
    setTheme((prev) => (prev === 'academic-dark' ? 'academic-light' : 'academic-dark'))
  }

  async function handleGenerate() {
    const trimmed = url.trim()
    setError('')
    setStatusMessage('')

    if (!trimmed) {
      setError('Please paste a YouTube URL to get started.')
      return
    }
    if (!trimmed.includes('youtube.com') && !trimmed.includes('youtu.be')) {
      setError("That doesn't look like a YouTube link. Please check and try again.")
      return
    }

    setLoading(true)
    setResults(null)
    try {
      const data = await generateNotes(trimmed, language)
      setResults(data)
      if (data.status) setStatusMessage(data.status)
    } catch (err) {
      setError(extractErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <ThemeToggle theme={theme} onToggle={toggleTheme} />
      <Hero />

      <SearchForm
        url={url}
        setUrl={setUrl}
        language={language}
        setLanguage={setLanguage}
        languages={languages}
        onSubmit={handleGenerate}
        loading={loading}
      />

      {error && <div className="alert alert-error">{error}</div>}

      {loading && (
        <div className="loading-row">
          <span className="spinner" />
          <span>Understanding video (captions, then audio, then visuals if needed)…</span>
        </div>
      )}

      {!loading && statusMessage && !error && (
        <div className="alert">{statusMessage}</div>
      )}

      {!loading && results && <ResultsPanel results={results} theme={theme} />}
    </div>
  )
}
