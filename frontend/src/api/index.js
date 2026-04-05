const API_BASE = import.meta.env.VITE_API_URL || ''

export async function analyzeUrl(url) {
  const response = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.error || 'Analysis failed')
  }

  return response.json()
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/api/health`)
  return response.json()
}
