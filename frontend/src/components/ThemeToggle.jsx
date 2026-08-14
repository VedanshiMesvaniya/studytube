export default function ThemeToggle({ theme, onToggle }) {
  const isDark = theme === 'academic-dark'
  return (
    <button className="theme-toggle" onClick={onToggle} type="button">
      <span>{isDark ? '◐ Dark' : '○ Light'}</span>
    </button>
  )
}
