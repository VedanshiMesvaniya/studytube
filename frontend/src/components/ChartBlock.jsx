import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'

const PALETTE_DARK = ['#dedede', '#c4c4c4', '#8e8e8e', '#a8a8a8', '#6f6f6f', '#bdbdbd', '#565656', '#e8e8e8']
const PALETTE_LIGHT = ['#1a1a1a', '#3a3a3a', '#5c5c5c', '#767676', '#8e8e8e', '#4b4b4b', '#2b2b2b', '#9a9a9a']

export default function ChartBlock({ type, title, labels, values, theme }) {
  const isDark = theme === 'academic-dark'
  const palette = isDark ? PALETTE_DARK : PALETTE_LIGHT
  const gridColor = isDark ? '#2a2a2a' : '#dcdcdc'
  const textColor = isDark ? '#c8c8c8' : '#4b4b4b'

  const data = labels.map((label, i) => ({ name: label, value: values[i] }))

  return (
    <div className="visual-card">
      <div className="visual-title">{title || 'Data from Video'}</div>
      <ResponsiveContainer width="100%" height={320}>
        {type === 'line' ? (
          <LineChart data={data}>
            <CartesianGrid stroke={gridColor} strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" stroke={textColor} fontSize={12} />
            <YAxis stroke={textColor} fontSize={12} />
            <Tooltip
              contentStyle={{ background: isDark ? '#1b1b1b' : '#ffffff', border: `1px solid ${gridColor}`, borderRadius: 10 }}
              labelStyle={{ color: textColor }}
            />
            <Line type="monotone" dataKey="value" stroke={palette[0]} strokeWidth={2.5} dot={{ r: 4 }} />
          </LineChart>
        ) : type === 'pie' ? (
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={110} label>
              {data.map((_, i) => (
                <Cell key={i} fill={palette[i % palette.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ background: isDark ? '#1b1b1b' : '#ffffff', border: `1px solid ${gridColor}`, borderRadius: 10 }} />
          </PieChart>
        ) : (
          <BarChart data={data}>
            <CartesianGrid stroke={gridColor} strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="name" stroke={textColor} fontSize={12} />
            <YAxis stroke={textColor} fontSize={12} />
            <Tooltip
              contentStyle={{ background: isDark ? '#1b1b1b' : '#ffffff', border: `1px solid ${gridColor}`, borderRadius: 10 }}
              labelStyle={{ color: textColor }}
              cursor={{ fill: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)' }}
            />
            <Bar dataKey="value" radius={[6, 6, 0, 0]}>
              {data.map((_, i) => (
                <Cell key={i} fill={palette[i % palette.length]} />
              ))}
            </Bar>
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  )
}
