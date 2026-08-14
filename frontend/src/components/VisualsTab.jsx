import MermaidDiagram from './MermaidDiagram'
import ChartBlock from './ChartBlock'

export default function VisualsTab({ visuals, theme }) {
  const v = visuals || {}
  const hasFlowchart = v.has_flowchart && v.flowchart_mermaid
  const hasChart =
    v.has_chart &&
    v.chart_labels &&
    v.chart_values &&
    v.chart_labels.length > 0 &&
    v.chart_labels.length === v.chart_values.length
  const hasMindmap = v.has_mindmap && v.mindmap_nodes && v.mindmap_nodes.length > 0

  const foundAny = hasFlowchart || hasChart || hasMindmap

  let mindmapCode = ''
  if (hasMindmap) {
    const center = v.mindmap_title || 'Main Topic'
    mindmapCode = `mindmap\n  root((${center}))\n` + v.mindmap_nodes.slice(0, 8).map((n) => `    ${n}`).join('\n')
  }

  if (!foundAny) {
    return (
      <div className="tab-panel">
        <div className="no-visual">
          No diagrams or charts detected in this video. Try a tutorial, lecture, or data-focused video for best results.
        </div>
      </div>
    )
  }

  return (
    <div className="tab-panel">
      {hasFlowchart && (
        <div className="visual-card">
          <div className="visual-title">{v.flowchart_title || 'Process Flow'}</div>
          <MermaidDiagram code={v.flowchart_mermaid} theme={theme} />
        </div>
      )}

      {hasChart && (
        <ChartBlock
          type={v.chart_type || 'bar'}
          title={v.chart_title}
          labels={v.chart_labels}
          values={v.chart_values}
          theme={theme}
        />
      )}

      {hasMindmap && (
        <div className="visual-card">
          <div className="visual-title">{v.mindmap_title || 'Concept Map'}</div>
          <MermaidDiagram code={mindmapCode} theme={theme} />
        </div>
      )}
    </div>
  )
}
