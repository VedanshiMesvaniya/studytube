import { useState } from 'react'
import QuizTab from './QuizTab'
import FlashcardsTab from './FlashcardsTab'
import VisualsTab from './VisualsTab'
import { downloadNotesPdf, extractErrorMessage } from '../api/client'

const TABS = ['Summary', 'Key Points', 'Q & A', 'Quiz', 'Flashcards', 'Visuals']

export default function ResultsPanel({ results, theme }) {
  const [activeTab, setActiveTab] = useState('Summary')
  const [pdfLoading, setPdfLoading] = useState(false)
  const [pdfError, setPdfError] = useState('')

  async function handleDownloadPdf() {
    setPdfLoading(true)
    setPdfError('')
    try {
      const blob = await downloadNotesPdf({
        url: results.url,
        summary: results.summary,
        keypoints: results.keypoints,
        qa: results.qa,
        quiz_text: results.quiz_text,
        flashcards_text: results.flashcards_text,
      })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = 'studytube_notes.pdf'
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      setPdfError(extractErrorMessage(err))
    } finally {
      setPdfLoading(false)
    }
  }

  return (
    <div>
      <div className="word-count">{results.word_count.toLocaleString()} words</div>

      <div className="tabs">
        <div className="tab-list">
          {TABS.map((tab) => (
            <button
              key={tab}
              type="button"
              className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </div>

        {activeTab === 'Summary' && (
          <div className="tab-panel">
            <div className="section-badge">Summary</div>
            <br />
            {results.summary}
          </div>
        )}

        {activeTab === 'Key Points' && (
          <div className="tab-panel">
            <div className="section-badge">Key Points</div>
            <br />
            {results.keypoints}
          </div>
        )}

        {activeTab === 'Q & A' && (
          <div className="tab-panel">
            <div className="section-badge">Q & A</div>
            <br />
            {results.qa}
          </div>
        )}

        {activeTab === 'Quiz' && (
          <QuizTab questions={results.quiz_questions} rawText={results.quiz_text} />
        )}

        {activeTab === 'Flashcards' && (
          <FlashcardsTab pairs={results.flashcard_pairs} rawText={results.flashcards_text} />
        )}

        {activeTab === 'Visuals' && (
          <VisualsTab visuals={results.visuals} theme={theme} />
        )}
      </div>

      <hr className="divider" />

      <button className="btn-outline" style={{ width: '100%' }} onClick={handleDownloadPdf} disabled={pdfLoading} type="button">
        {pdfLoading ? 'Preparing PDF…' : 'Download Notes as PDF'}
      </button>
      {pdfError && <div className="alert alert-error" style={{ marginTop: 12 }}>{pdfError}</div>}
    </div>
  )
}
