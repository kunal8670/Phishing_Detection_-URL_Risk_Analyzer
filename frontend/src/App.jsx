import { useState } from 'react'
import { analyzeUrl } from './api'

const riskTags = [
  { label: 'Safe', max: 25, color: '#22c55e', bg: '#22c55e', lightBg: '#dcfce7' },
  { label: 'Suspicious', max: 50, color: '#eab308', bg: '#eab308', lightBg: '#fef9c3' },
  { label: 'Warning', max: 75, color: '#f97316', bg: '#f97316', lightBg: '#ffedd5' },
  { label: 'Risky', max: 100, color: '#ef4444', bg: '#ef4444', lightBg: '#fee2e2' },
]

function getRiskTag(score) {
  return riskTags.find(t => score <= t.max) || riskTags[riskTags.length - 1]
}

function RiskGauge({ score }) {
  const circumference = 2 * Math.PI * 54
  const strokeDashoffset = circumference - (score / 100) * circumference
  const tag = getRiskTag(score)

  return (
    <div className="flex flex-col items-center">
      <svg width="140" height="140" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="54" fill="none" stroke="#e5e7eb" strokeWidth="10" />
        <circle
          cx="60" cy="60" r="54" fill="none" stroke={tag.color} strokeWidth="10"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform="rotate(-90 60 60)"
          className="transition-all duration-1000 ease-out"
        />
        <text x="60" y="55" textAnchor="middle" className="text-3xl font-bold" fill={tag.color}>{Math.round(score)}</text>
        <text x="60" y="75" textAnchor="middle" className="text-xs" fill="#6b7280">/ 100</text>
      </svg>
    </div>
  )
}

function RiskIndicatorBar({ score }) {
  const tag = getRiskTag(score)
  const markerPos = Math.min(score, 100)

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Risk Level</h3>

      <div className="flex items-center gap-1 mb-2">
        {riskTags.map((t, i) => (
          <div key={t.label} className="flex-1 text-center">
            <div className="text-sm font-semibold" style={{ color: t.label === tag.label ? t.color : '#9ca3af' }}>
              {t.label}
            </div>
            <div className="text-xs" style={{ color: t.label === tag.label ? t.color : '#d1d5db' }}>
              {i === 0 ? `0–${t.max}` : `${riskTags[i - 1].max + 1}–${t.max}`}
            </div>
          </div>
        ))}
      </div>

      <div className="relative h-3 rounded-full overflow-hidden flex mb-6 border border-gray-200">
        {riskTags.map(t => (
          <div key={t.label} className="flex-1 transition-colors duration-500" style={{ backgroundColor: t.label === tag.label ? t.bg : t.lightBg }} />
        ))}
        <div
          className="absolute top-0 h-full w-1 bg-gray-800 shadow-lg transition-all duration-1000 ease-out"
          style={{ left: `${markerPos}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-500">Score: <span className="font-bold" style={{ color: tag.color }}>{Math.round(score)}</span></span>
        <span className="font-bold px-3 py-1 rounded-full text-white" style={{ backgroundColor: tag.color }}>
          {tag.label}
        </span>
      </div>
    </div>
  )
}

function FeatureTable({ features }) {
  const featureLabels = {
    URLLength: 'URL Length',
    DomainLength: 'Domain Length',
    IsDomainIP: 'Domain is IP',
    TLDLength: 'TLD Length',
    NoOfSubDomain: 'Subdomains Count',
    NoOfLettersInURL: 'Letters in URL',
    LetterRatioInURL: 'Letter Ratio',
    NoOfDigitsInURL: 'Digits in URL',
    DigitRatioInURL: 'Digit Ratio',
    NoOfEqualsInURL: 'Equals Signs',
    NoOfQMarkInURL: 'Question Marks',
    NoOfAmpersandInURL: 'Ampersands',
    NoOfOtherSpecialCharsInURL: 'Special Chars',
    SpecialCharRatioInURL: 'Special Char Ratio',
    HasObfuscation: 'Has Obfuscation',
    NoOfObfuscatedChar: 'Obfuscated Chars',
    ObfuscationRatio: 'Obfuscation Ratio',
    IsHTTPS: 'Uses HTTPS',
    Bank: 'Bank Keywords',
    Pay: 'Pay Keywords',
    Crypto: 'Crypto Keywords',
    SuspiciousWords: 'Suspicious Words',
    URLDepth: 'URL Depth',
    AvgTokenLength: 'Avg Token Length',
  }

  return (
    <div className="bg-white rounded-xl shadow p-6">
      <h3 className="text-lg font-semibold mb-4">Extracted Features</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {Object.entries(features).map(([key, value]) => (
          <div key={key} className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-gray-500">{featureLabels[key] || key}</div>
            <div className="text-lg font-medium">{value}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ResultCard({ result }) {
  const { risk_score, risk_level, ml_prediction, ml_confidence, threat_intel, url, domain, breakdown, features } = result

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow p-8 flex flex-col md:flex-row items-center gap-8">
        <RiskGauge score={risk_score} />
        <div className="flex-1 text-center md:text-left">
          <h2 className="text-2xl font-bold mb-2">Analysis Result</h2>
          <p className="text-gray-600 mb-2 truncate">{url}</p>
          <p className="text-sm text-gray-500 mb-4">Domain: {domain}</p>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">ML Prediction:</span>
              <span className="ml-2 font-medium capitalize">{ml_prediction}</span>
              {ml_confidence && <span className="ml-1 text-gray-400">({(ml_confidence * 100).toFixed(1)}%)</span>}
            </div>
            <div>
              <span className="text-gray-500">Threat Intel:</span>
              <span className={`ml-2 font-medium ${threat_intel.found ? 'text-red-600' : 'text-green-600'}`}>
                {threat_intel.found
                  ? `Found in ${threat_intel.sources.map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(', ')}`
                  : 'Clean — not in any threat feed'}
              </span>
            </div>
            <div>
              <span className="text-gray-500">ML Score:</span>
              <span className="ml-2 font-medium">{breakdown.ml_score !== null ? `${breakdown.ml_score.toFixed(1)}%` : 'N/A'}</span>
            </div>
            <div>
              <span className="text-gray-500">Threat Score:</span>
              <span className="ml-2 font-medium">{breakdown.threat_score.toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>

      <RiskIndicatorBar score={risk_score} />

      <FeatureTable features={features} />
    </div>
  )
}

export default function App() {
  const [url, setUrl] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await analyzeUrl(url)
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-3">Phishing Detection</h1>
          <p className="text-blue-200 text-lg">URL Risk Analyzer powered by Random Forest ML & Threat Intelligence</p>
        </div>

        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter URL to analyze (e.g., https://example.com)"
              className="flex-1 px-5 py-4 rounded-xl text-lg bg-white/10 backdrop-blur border border-white/20 text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-4 bg-blue-500 hover:bg-blue-600 disabled:bg-blue-400 text-white font-semibold rounded-xl text-lg transition-colors"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </form>

        {error && (
          <div className="bg-red-500/20 border border-red-500/50 text-red-200 rounded-xl p-4 mb-6">
            {error}
          </div>
        )}

        {result && <ResultCard result={result} />}

        {!result && !loading && (
          <div className="text-center text-blue-300/60 mt-16">
            <p className="text-lg">Enter a URL above to check its risk level</p>
            <div className="mt-6 grid grid-cols-3 gap-6 max-w-lg mx-auto text-sm">
              <div className="bg-white/5 rounded-lg p-4">
                <div className="text-green-400 font-semibold text-2xl">ML</div>
                <div>Random Forest</div>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <div className="text-blue-400 font-semibold text-2xl">24</div>
                <div>URL Features</div>
              </div>
              <div className="bg-white/5 rounded-lg p-4">
                <div className="text-yellow-400 font-semibold text-2xl">2</div>
                <div>Threat Feeds</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
