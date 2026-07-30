import { useState, useCallback, useRef } from 'react'
import './App.css'

/* ─── SVG icon components ─────────────────────────────────────── */
const IconFilm = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"/>
    <line x1="7" y1="2" x2="7" y2="22"/><line x1="17" y1="2" x2="17" y2="22"/>
    <line x1="2" y1="12" x2="22" y2="12"/><line x1="2" y1="7" x2="7" y2="7"/>
    <line x1="2" y1="17" x2="7" y2="17"/><line x1="17" y1="17" x2="22" y2="17"/>
    <line x1="17" y1="7" x2="22" y2="7"/>
  </svg>
)

const IconSparkles = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M12 3L13.5 8.5L19 10L13.5 11.5L12 17L10.5 11.5L5 10L10.5 8.5Z"/>
    <path d="M19 3L19.75 5.25L22 6L19.75 6.75L19 9L18.25 6.75L16 6L18.25 5.25Z"/>
    <path d="M5 17L5.5 18.5L7 19L5.5 19.5L5 21L4.5 19.5L3 19L4.5 18.5Z"/>
  </svg>
)

const IconZap = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
  </svg>
)

const IconPenTool = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/>
    <path d="M2 2l7.586 7.586"/><circle cx="11" cy="11" r="2"/>
  </svg>
)

const IconVideo = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
  </svg>
)

const IconHash = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="15" x2="20" y2="15"/>
    <line x1="10" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="14" y2="21"/>
  </svg>
)

const IconImage = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
    <circle cx="8.5" cy="8.5" r="1.5"/>
    <polyline points="21 15 16 10 5 21"/>
  </svg>
)

const IconArrowRight = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
  </svg>
)

const IconMonitor = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
    <line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
  </svg>
)

const IconMic = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/>
    <line x1="8" y1="23" x2="16" y2="23"/>
  </svg>
)

const IconSpinner = () => (
  <svg className="rc-spinner" viewBox="0 0 24 24" fill="none" aria-hidden="true">
    <circle className="rc-spinner-track" cx="12" cy="12" r="9" stroke="rgba(255,255,255,0.20)" strokeWidth="2.5"/>
    <circle className="rc-spinner-arc"   cx="12" cy="12" r="9" stroke="#ffffff"               strokeWidth="2.5"
      strokeLinecap="round"
      strokeDasharray="56.55"
      strokeDashoffset="42"
    />
  </svg>
)

const IconDownload = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="7 10 12 15 17 10"/>
    <line x1="12" y1="15" x2="12" y2="3"/>
  </svg>
)

const IconCopy = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
  </svg>
)

const IconCheck = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
)

/* ─── Constants ───────────────────────────────────────────────── */
const PLATFORMS = ['Instagram', 'TikTok', 'LinkedIn', 'YouTube Shorts']
const TONES = ['Professional', 'Fun', 'Cute', 'Inspirational', 'Informative']

const RESULT_CARDS = [
  { key: 'caption',  label: 'Caption',        Icon: IconPenTool,   wide: false, placeholder: 'Your AI-generated caption will appear here.' },
  { key: 'script',   label: 'Video Script',   Icon: IconVideo,     wide: false, placeholder: 'Your AI-generated video script will appear here.' },
  { key: 'hashtags', label: 'Hashtags',        Icon: IconHash,      wide: false, placeholder: 'Your AI-generated hashtags will appear here.' },
  { key: 'visual',   label: 'Visual Concept', Icon: IconImage,     wide: false, placeholder: 'Your AI-generated visual concept will appear here.' },
  { key: 'cta',      label: 'Call to Action', Icon: IconArrowRight, wide: true,  placeholder: 'Your AI-generated call to action will appear here.' },
]

/* ─── useCopyCard hook ────────────────────────────────────────── */
function useCopyCard() {
  const [copiedKey, setCopiedKey] = useState(null)
  const timerRef = useRef(null)

  const copy = useCallback((key, text) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedKey(key)
      clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => setCopiedKey(null), 2000)
    })
  }, [])

  return { copiedKey, copy }
}

/* ─── App ─────────────────────────────────────────────────────── */
function App() {
  const [idea, setIdea] = useState('')
  const [platform, setPlatform] = useState(PLATFORMS[0])
  const [tone, setTone] = useState(TONES[0])
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [generated, setGenerated] = useState(false)
  const { copiedKey, copy } = useCopyCard()

  function handleDownload() {
    const divider = '─'.repeat(48)
    const text = [
      '╔════════════════════════════════════════════════╗',
      '║           REELCRAFT AI — Generated Content     ║',
      '╚════════════════════════════════════════════════╝',
      '',
      `  Idea      : ${idea}`,
      `  Platform  : ${platform}`,
      `  Tone      : ${tone}`,
      '',
      divider,
      '  CAPTION',
      divider,
      results.caption,
      '',
      divider,
      '  VIDEO SCRIPT',
      divider,
      results.script,
      '',
      divider,
      '  HASHTAGS',
      divider,
      results.hashtags,
      '',
      divider,
      '  VISUAL CONCEPT',
      divider,
      results.visual,
      '',
      divider,
      '  CALL TO ACTION',
      divider,
      results.cta,
      '',
      divider,
      `  Generated by ReelCraft AI · ${new Date().toLocaleString()}`,
      divider,
    ].join('\n')

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `reelcraft-${platform.toLowerCase().replace(/\s+/g, '-')}-${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  async function handleGenerate() {
  if (!idea.trim()) return

  setLoading(true)
  setGenerated(false)

  try {
    const response = await fetch('http://127.0.0.1:5000/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        idea: idea.trim(),
        platform,
        tone,
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Content generation failed')
    }

    setResults({
  caption: data.caption,
  script: data.videoScript,
  hashtags: data.hashtags,
  visual: data.visualConcept,
  cta: data.callToAction,
})
    setGenerated(true)
  } catch (error) {
    console.error('Generation error:', error)
    alert(`Generation failed: ${error.message}`)
  } finally {
    setLoading(false)
  }
}

  return (
    <div className="rc-page">

      {/* ── Header ─────────────────────────────────────────────── */}
      <header className="rc-header">
        <div className="rc-header-inner">
          <a href="/" className="rc-logo">
            <span className="rc-logo-icon"><IconFilm /></span>
            <span className="rc-logo-text">ReelCraft AI</span>
          </a>
          <nav className="rc-nav">
            <a href="#generate" className="rc-nav-link">Generate</a>
            <a href="#results" className="rc-nav-link">Results</a>
          </nav>
        </div>
      </header>

      <main className="rc-main">

        {/* ── Hero ───────────────────────────────────────────────── */}
        <section className="rc-hero">
          <div className="rc-hero-badge">
            <IconSparkles />
            AI-Powered Content Studio
          </div>
          <h1 className="rc-title">ReelCraft AI</h1>
          <p className="rc-subtitle">Turn one idea into social media content using AI</p>
        </section>

        {/* ── Two-column workspace ───────────────────────────────── */}
        <div className="rc-workspace">

          {/* Left — Input panel */}
          <section id="generate" className="rc-panel">
            <div className="rc-panel-inner">

              <p className="rc-panel-title">
                <IconZap />
                Describe your content idea
              </p>

              <div className="rc-divider" />

              <div className="rc-field">
                <label className="rc-label rc-label-with-icon" htmlFor="idea">
                  <IconMic />
                  Your idea
                </label>
                <textarea
                  id="idea"
                  className="rc-textarea"
                  rows={5}
                  placeholder="e.g. A morning routine that boosts productivity and creativity for remote workers…"
                  value={idea}
                  onChange={e => setIdea(e.target.value)}
                />
              </div>

              <div className="rc-row">
                <div className="rc-field rc-field--half">
                  <label className="rc-label rc-label-with-icon" htmlFor="platform">
                    <IconMonitor />
                    Platform
                  </label>
                  <select id="platform" className="rc-select" value={platform} onChange={e => setPlatform(e.target.value)}>
                    {PLATFORMS.map(p => <option key={p}>{p}</option>)}
                  </select>
                </div>

                <div className="rc-field rc-field--half">
                  <label className="rc-label rc-label-with-icon" htmlFor="tone">
                    <IconSparkles />
                    Tone
                  </label>
                  <select id="tone" className="rc-select" value={tone} onChange={e => setTone(e.target.value)}>
                    {TONES.map(t => <option key={t}>{t}</option>)}
                  </select>
                </div>
              </div>

              <button
                className={`rc-btn${loading ? ' rc-btn--loading' : ''}`}
                onClick={handleGenerate}
                disabled={loading || !idea.trim()}
              >
                {loading
                  ? <><IconSpinner />Generating...</>
                  : <><span className="rc-btn-icon"><IconSparkles /></span>Generate Content</>
                }
              </button>

            </div>
          </section>

          {/* Right — Result cards */}
          <section id="results" className="rc-results-col">
            <div className="rc-results-heading">
              <h2 className={`rc-results-title${generated ? ' rc-results-title--visible' : ''}`}>
                Generated Content
              </h2>
              <span className={`rc-results-count${generated ? ' rc-results-count--visible' : ''}`}>
                {RESULT_CARDS.length} items
              </span>
              {generated && (
                <button className="rc-download-btn" onClick={handleDownload} title="Download as text file">
                  <IconDownload />
                  Download
                </button>
              )}
            </div>

            <div className="rc-cards">
              {RESULT_CARDS.map(({ key, label, Icon, wide, placeholder }) => {
                const content = results ? results[key] : null
                const isCopied = copiedKey === key
                return (
                  <div
                    key={key}
                    className={[
                      'rc-card',
                      generated ? 'rc-card--filled' : '',
                      wide ? 'rc-card--wide' : '',
                    ].filter(Boolean).join(' ')}
                  >
                    <div className="rc-card-header">
                      <div className="rc-card-header-left">
                        <span className="rc-card-icon"><Icon /></span>
                        <span className="rc-card-label">{label}</span>
                      </div>
                      {content && (
                        <button
                          className={`rc-copy-btn${isCopied ? ' rc-copy-btn--copied' : ''}`}
                          onClick={() => copy(key, content)}
                          aria-label={isCopied ? 'Copied!' : `Copy ${label}`}
                          title={isCopied ? 'Copied!' : 'Copy to clipboard'}
                        >
                          {isCopied ? <IconCheck /> : <IconCopy />}
                          <span>{isCopied ? 'Copied!' : 'Copy'}</span>
                        </button>
                      )}
                    </div>
                    <p className="rc-card-body">
                      {content ?? placeholder}
                    </p>
                  </div>
                )
              })}
            </div>
          </section>

        </div>{/* end .rc-workspace */}
      </main>

      <footer className="rc-footer">
        <p>© {new Date().getFullYear()} <span>ReelCraft AI</span> — Powered by artificial intelligence</p>
      </footer>

    </div>
  )
}

export default App
