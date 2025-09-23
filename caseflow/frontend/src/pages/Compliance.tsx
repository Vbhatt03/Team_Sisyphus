import React, { useEffect, useState } from 'react'
import { useAppStore } from '../store'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '../store'

const Compliance: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [generatingDiary, setGeneratingDiary] = useState(false)
  const [rawMarkdown, setRawMarkdown] = useState('')

  const {
    currentCaseId,
    checklistItems,
    loadCompliance,
    updateChecklistItem
  } = useAppStore()

  const navigate = useNavigate()

  useEffect(() => {
    const loadAll = async () => {
      if (!currentCaseId) return
      await loadCompliance()
      try {
        const res = await fetch(`${apiClient.baseUrl}/api/compliance/raw?case_id=${currentCaseId}`, {
          headers: {
            // attempt to use Authorization header if token is stored internally
          }
        })
        if (res.ok) {
          const data = await res.json()
            ;(data && data.content) && setRawMarkdown(data.content)
        }
      } catch (_) { /* ignore raw markdown load failure */ }
    }
    loadAll()
  }, [currentCaseId, loadCompliance])

  const handleGenerateCompliance = async () => {
    if (!currentCaseId) return

    setLoading(true)
    setError('')

    try {
      await apiClient.runCompliance(currentCaseId)
      await loadCompliance()
    } catch (err) {
      setError('Failed to generate compliance checklist')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateCaseDiary = async () => {
    if (!currentCaseId) return

    setGeneratingDiary(true)
    setError('')

    try {
      await apiClient.generateCaseDiary(currentCaseId)
      navigate('/case-diary')
    } catch (err) {
      setError('Failed to generate case diary')
    } finally {
      setGeneratingDiary(false)
    }
  }

  const handleCheckboxChange = async (itemId: number, checked: boolean) => {
    try {
      await updateChecklistItem(itemId, checked)
    } catch (err) {
      setError('Failed to update checklist item')
    }
  }

  const handleTextEdit = async (itemId: number, text: string) => {
    try {
      await updateChecklistItem(itemId, undefined, text)
    } catch (err) {
      setError('Failed to update checklist item')
    }
  }

  const groupedItems = checklistItems.reduce((groups, item) => {
    const section = item.section || 'General'
    if (!groups[section]) {
      groups[section] = []
    }
    groups[section].push(item)
    return groups
  }, {} as Record<string, typeof checklistItems>)

  const completedCount = checklistItems.filter(item => item.checked).length
  const totalCount = checklistItems.length
  const completionPercentage = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0

  return (
    <div className="min-h-screen flex items-start justify-center py-10">
      <div className="caseflow-container w-full max-w-6xl mx-4">
        <div className="caseflow-header">
          <h2 className="caseflow-title">Compliance Checklist</h2>
          <p className="caseflow-subtitle">SOP compliance verification for legal case processing</p>
        </div>
        <div className="form-container" style={{ margin: '0' }}>
          {/* Header */}
          <div className="mb-6 -mt-4">
            {checklistItems.length === 0 && (
              <div className="flex justify-end">
                <button
                  onClick={handleGenerateCompliance}
                  disabled={loading}
                  className="btn-primary disabled:opacity-50"
                >
                  {loading ? 'Generating...' : 'Generate Compliance Checklist'}
                </button>
              </div>
            )}
            {checklistItems.length > 0 && (
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-white/60 p-4 rounded-lg shadow-sm border border-gray-200">
                <div className="flex items-center space-x-4">
                  <div className="text-sm text-gray-700 font-medium">
                    {completedCount} of {totalCount} items completed ({completionPercentage}%)
                  </div>
                  <div className="w-48 bg-gray-200 rounded-full h-2">
                    <div className="bg-green-500 h-2 rounded-full transition-all duration-300" style={{ width: `${completionPercentage}%` }}></div>
                  </div>
                </div>
                <button
                  onClick={handleGenerateCaseDiary}
                  disabled={generatingDiary}
                  className="btn-secondary disabled:opacity-50"
                >
                  {generatingDiary ? 'Generating...' : 'Generate Case Diary'}
                </button>
              </div>
            )}
          </div>

          {/* Content */}
          <div>
            {error && (
              <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}

            {checklistItems.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-500 mb-4">
                  No compliance checklist found. Generate one from your parsed documents.
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {rawMarkdown && (
                  <div className="bg-white/70 border border-gray-200 rounded-lg p-5 shadow-sm fade-in">
                    <div className="prose max-w-none">
                      {(() => {
                        const lines = rawMarkdown.split('\n')
                        const preview: string[] = []
                        for (const l of lines) {
                          if (preview.length >= 12) break
                          // Stop early if we reach first checklist bullet
                          if (/^- \[[x ]\]/i.test(l)) break
                          preview.push(l)
                        }
                        return preview.map((line, idx) => {
                          const trimmed = line.trim()
                          if (!trimmed) return <div key={idx} style={{ height: '4px' }} />
                          const isHeader = /^#+/.test(trimmed)
                          const isNote = /^>/.test(trimmed)
                          return (
                            <p
                              key={idx}
                              className={
                                isHeader
                                  ? 'font-semibold text-gray-800 text-lg'
                                  : isNote
                                    ? 'text-sm italic text-gray-600'
                                    : 'text-sm text-gray-700'
                              }
                            >
                              {trimmed.replace(/^#+\s*/, '')}
                            </p>
                          )
                        })
                      })()}
                    </div>
                  </div>
                )}
                {Object.entries(groupedItems).map(([section, items]) => (
                  <div key={section} className="border rounded-lg">
                    <div className="bg-gray-50 px-4 py-3 border-b">
                      <h3 className="font-medium text-gray-900">{section}</h3>
                      <div className="text-sm text-gray-500">
                        {items.filter(item => item.checked).length} of {items.length} completed
                      </div>
                    </div>
                    
                    <div className="p-4 space-y-4">
                      {items.map(item => (
                        <ChecklistItem
                          key={item.id}
                          item={item}
                          onCheckboxChange={handleCheckboxChange}
                          onTextEdit={handleTextEdit}
                        />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

interface ChecklistItemProps {
  item: any
  onCheckboxChange: (id: number, checked: boolean) => void
  onTextEdit: (id: number, text: string) => void
}

const ChecklistItem: React.FC<ChecklistItemProps> = ({ item, onCheckboxChange, onTextEdit }) => {
  const [editing, setEditing] = useState(false)
  const [editText, setEditText] = useState(item.text)

  const handleSave = () => {
    onTextEdit(item.id, editText)
    setEditing(false)
  }

  const handleCancel = () => {
    setEditText(item.text)
    setEditing(false)
  }

  return (
    <div className={`flex items-start space-x-3 p-3 rounded-md border ${
      item.checked ? 'bg-green-50 border-green-200' : 'bg-white border-gray-200'
    }`}>
      <input
        type="checkbox"
        checked={item.checked}
        onChange={(e) => onCheckboxChange(item.id, e.target.checked)}
        className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
      />
      
      <div className="flex-1 min-w-0">
        {editing ? (
          <div className="space-y-2">
            <textarea
              value={editText}
              onChange={(e) => setEditText(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows={3}
            />
            <div className="flex space-x-2">
              <button
                onClick={handleSave}
                className="px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
              >
                Save
              </button>
              <button
                onClick={handleCancel}
                className="px-3 py-1 bg-gray-300 text-gray-700 text-sm rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="group">
            <p className={`text-sm ${item.checked ? 'line-through text-gray-500' : 'text-gray-900'}`}>
              {item.text}
            </p>
            <button
              onClick={() => setEditing(true)}
              className="mt-1 text-xs text-indigo-600 hover:text-indigo-800 opacity-0 group-hover:opacity-100 transition-opacity"
            >
              Edit
            </button>
          </div>
        )}
      </div>
      
      {item.checked && (
        <div className="text-green-600">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        </div>
      )}
    </div>
  )
}

export default Compliance