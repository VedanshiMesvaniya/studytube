export default function SearchForm({
  url,
  setUrl,
  language,
  setLanguage,
  languages,
  onSubmit,
  loading,
}) {
  function handleSubmit(e) {
    e.preventDefault()
    onSubmit()
  }

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <div className="search-row">
        <input
          className="search-input"
          type="text"
          placeholder="youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={loading}
        />
        <select
          className="search-select"
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          disabled={loading}
        >
          {languages.map((lang) => (
            <option key={lang} value={lang}>
              {lang}
            </option>
          ))}
        </select>
      </div>
      <div className="search-actions">
        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? 'Generating…' : 'Generate Study Notes'}
        </button>
      </div>
    </form>
  )
}
