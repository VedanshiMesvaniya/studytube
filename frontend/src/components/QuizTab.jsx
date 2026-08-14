import { useState } from 'react'

export default function QuizTab({ questions, rawText }) {
  const [answers, setAnswers] = useState({})
  const [submitted, setSubmitted] = useState(false)

  if (!questions || questions.length === 0) {
    return <div className="tab-panel">{rawText || 'No quiz was generated for this video.'}</div>
  }

  function selectAnswer(qIndex, key) {
    if (submitted) return
    setAnswers((prev) => ({ ...prev, [qIndex]: key }))
  }

  function reset() {
    setAnswers({})
    setSubmitted(false)
  }

  return (
    <div className="tab-panel">
      {questions.map((q, i) => (
        <div className="quiz-q" key={i}>
          <p className="quiz-question">
            Q{i + 1}. {q.question}
          </p>
          {Object.entries(q.options).map(([key, value]) => (
            <label className="quiz-option" key={key}>
              <input
                type="radio"
                name={`quiz-${i}`}
                checked={answers[i] === key}
                onChange={() => selectAnswer(i, key)}
                disabled={submitted}
              />
              <span>
                {key}) {value}
              </span>
            </label>
          ))}
          {submitted && answers[i] && (
            answers[i] === q.answer ? (
              <div className="correct-answer">Correct</div>
            ) : (
              <div className="wrong-answer">
                Wrong — correct answer: {q.answer}) {q.options[q.answer]}
              </div>
            )
          )}
        </div>
      ))}

      <div className="quiz-actions">
        <button className="btn-primary" onClick={() => setSubmitted(true)} disabled={submitted} type="button">
          Submit Answers
        </button>
        <button className="btn-outline" onClick={reset} type="button">
          Reset Quiz
        </button>
      </div>
    </div>
  )
}
