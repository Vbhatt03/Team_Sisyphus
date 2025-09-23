import React, { useEffect, useState } from 'react'
import { useAppStore } from '../store'
import { useNavigate } from 'react-router-dom'

const CaseDiary: React.FC = () => {
  const [content, setContent] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [generatingFinal, setGeneratingFinal] = useState(false)

  const {
    currentCaseId,
    currentDiaryPage,
    loadCaseDiaryPage,
    saveDiaryPage,
    nextDiaryPage,
    generateFinalReports
  } = useAppStore()

  const navigate = useNavigate()

  useEffect(() => {
    if (currentCaseId) {
      loadCaseDiaryPage(1)
    }
  }, [currentCaseId, loadCaseDiaryPage])

  useEffect(() => {
    if (currentDiaryPage) {
      setContent(currentDiaryPage.content)
    }
  }, [currentDiaryPage])

  const handleSave = async () => {
    if (!currentDiaryPage) return

    setSaving(true)
    setError('')

    try {
      await saveDiaryPage(content)
    } catch (err) {
      setError('Failed to save page')
    } finally {
      setSaving(false)
    }
  }

  const handleNext = async () => {
    setError('')

    try {
      await nextDiaryPage()
    } catch (err) {
      setError('No next page available')
    }
  }

  const handleGenerateFinal = async () => {
    setGeneratingFinal(true)
    setError('')

    try {
      await generateFinalReports()
      navigate('/final')
    } catch (err) {
      setError('Failed to generate final reports')
    } finally {
      setGeneratingFinal(false)
    }
  }

  if (!currentDiaryPage) {
    return <div className="min-h-screen flex items-center justify-center text-white">Loading case diary...</div>
  }

  return (
    <div className="min-h-screen flex items-start justify-center py-10">
      <div className="caseflow-container w-full max-w-6xl mx-4">
        <div className="caseflow-header">
          <h2 className="caseflow-title">Case Diary</h2>
          <p className="caseflow-subtitle">Page {currentDiaryPage.page_number} of {currentDiaryPage.total_pages}</p>
        </div>
        <div className="form-container" style={{ margin: 0 }}>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
            <div className="flex items-center space-x-4 bg-white/60 p-4 rounded-lg border border-gray-200 w-full">
              <div className="flex-1">
                <div className="text-sm text-gray-700 font-medium mb-2">Page Progress</div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-indigo-600 h-2 rounded-full transition-all duration-300" style={{ width: `${(currentDiaryPage.page_number / currentDiaryPage.total_pages) * 100}%` }}></div>
                </div>
              </div>
              <div className="text-sm text-gray-600 font-medium w-16 text-right">
                {Math.round((currentDiaryPage.page_number / currentDiaryPage.total_pages) * 100)}%
              </div>
            </div>
            <div className="flex space-x-2">
              <button onClick={handleSave} disabled={saving} className="btn-primary disabled:opacity-50">
                {saving ? 'Saving...' : 'Save'}
              </button>
              {currentDiaryPage.page_number < currentDiaryPage.total_pages && (
                <button onClick={handleNext} className="btn-secondary">Next Page</button>
              )}
              <button onClick={handleGenerateFinal} disabled={generatingFinal} className="btn-outline disabled:opacity-50">
                {generatingFinal ? 'Generating...' : 'Generate Final'}
              </button>
            </div>
          </div>

          {error && (
            <div className="mb-4 error-message">{error}</div>
          )}

            <label htmlFor="diary-content" className="block text-sm font-medium text-gray-700 mb-2">Case Diary Content</label>
            <textarea
              id="diary-content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full h-96 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono text-sm bg-white"
              placeholder="Enter case diary content..."
            />

          <div className="flex items-center justify-between text-xs text-gray-600 mt-3 bg-white/70 p-2 rounded border">
            <div>Last updated: {new Date(currentDiaryPage.updated_at).toLocaleString()}</div>
            <div className="flex space-x-4">
              <span>Chars: {content.length}</span>
              <span>Words: {content.split(/\s+/).filter(w => w).length}</span>
            </div>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {Array.from({ length: currentDiaryPage.total_pages }, (_, i) => i + 1).map(pageNum => (
              <button
                key={pageNum}
                onClick={() => loadCaseDiaryPage(pageNum)}
                className={`px-3 py-1 rounded-md text-sm font-medium ${
                  pageNum === currentDiaryPage.page_number
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {pageNum}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CaseDiary