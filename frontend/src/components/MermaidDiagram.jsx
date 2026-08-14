import { useEffect, useRef, useState } from 'react'
import mermaid from 'mermaid'

let idCounter = 0

export default function MermaidDiagram({ code, theme }) {
  const containerRef = useRef(null)
  const [error, setError] = useState(false)
  const isDark = theme === 'academic-dark'

  useEffect(() => {
    let cancelled = false
    idCounter += 1
    const id = `mermaid-${idCounter}`

    mermaid.initialize({
      startOnLoad: false,
      theme: isDark ? 'dark' : 'default',
      themeVariables: isDark
        ? {
            primaryColor: '#1b1b1b',
            primaryTextColor: '#ededed',
            primaryBorderColor: '#3a3a3a',
            lineColor: '#8e8e8e',
            background: '#111111',
            mainBkg: '#1b1b1b',
          }
        : {
            primaryColor: '#f5f5f5',
            primaryTextColor: '#1a1a1a',
            primaryBorderColor: '#bdbdbd',
            lineColor: '#767676',
            background: '#ffffff',
            mainBkg: '#ededed',
          },
    })

    mermaid
      .render(id, code)
      .then(({ svg }) => {
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg
        }
      })
      .catch(() => {
        if (!cancelled) setError(true)
      })

    return () => {
      cancelled = true
    }
  }, [code, isDark])

  if (error) return null
  return <div className="mermaid-wrap" ref={containerRef} />
}
