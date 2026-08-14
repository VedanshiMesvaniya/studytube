import { useState } from 'react'

export default function FlashcardsTab({ pairs, rawText }) {
  const [flipped, setFlipped] = useState({})

  if (!pairs || pairs.length === 0) {
    return <div className="tab-panel">{rawText || 'No flashcards were generated for this video.'}</div>
  }

  function toggle(i) {
    setFlipped((prev) => ({ ...prev, [i]: !prev[i] }))
  }

  return (
    <div className="tab-panel">
      <p className="flashcard-hint">— tap a card to flip —</p>
      <div className="flashcard-grid">
        {pairs.map((pair, i) => (
          <div
            key={i}
            className={`fc ${flipped[i] ? 'flipped' : ''}`}
            onClick={() => toggle(i)}
          >
            <div className="fc-inner">
              <div className="fc-front">
                <span className="fc-tag">concept</span>
                <p>{pair.front}</p>
              </div>
              <div className="fc-back">
                <span className="fc-tag">definition</span>
                <p>{pair.back}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
