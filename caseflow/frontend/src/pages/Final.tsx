import React, { useEffect, useState } from 'react'
import { useAppStore } from '../store'
import { apiClient } from '../store'

interface FileInfo {
  name: string
  size: number
  modified: string
  download_url: string
  direct_download_url?: string
  expires_at?: string
}

const Final: React.FC = () => {
  const [finalFiles, setFinalFiles] = useState<FileInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [previewContent, setPreviewContent] = useState<{ [key: string]: string }>({})

  const { currentCaseId } = useAppStore()

  useEffect(() => {
    if (currentCaseId) {
      loadFinalFiles()
    }
  }, [currentCaseId])

  const loadFinalFiles = async () => {
    if (!currentCaseId) return

    setLoading(true)
    setError('')

    try {
      const response = await apiClient.getFiles(currentCaseId, 'final')
      setFinalFiles(response.files || [])
    } catch (err) {
      setError('Failed to load final files')
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async (file: FileInfo) => {
    // Prefer signed direct link (no auth header). If absent, fallback to authenticated fetch.
    try {
      if (file.direct_download_url) {
        const full = `${apiClient.baseUrl}${file.direct_download_url}`
        const a = document.createElement('a')
        a.href = full
        a.download = file.name
        document.body.appendChild(a)
        a.click()
        a.remove()
        return
      }
      // Fallback (no direct link) - attempt unauthenticated (may 401)
      const full = `${apiClient.baseUrl}${file.download_url}`
      const res = await fetch(full)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = file.name
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (e) {
      console.error('Download failed', e)
      setError(`Download failed for ${file.name}`)
    }
  }

  const handlePreview = async (file: FileInfo) => {
    if (previewContent[file.name]) {
      // Toggle preview off if already showing
      setPreviewContent(prev => ({ ...prev, [file.name]: '' }))
      return
    }

    try {
      // For text files, fetch content for preview
      if (file.name.endsWith('.txt') || file.name.endsWith('.md')) {
        if (!file.direct_download_url) {
          setError('Preview unavailable: missing direct link.')
          return
        }
        const url = `${apiClient.baseUrl}${file.direct_download_url}`
        const response = await fetch(url)
        const text = await response.text()
        setPreviewContent(prev => ({ ...prev, [file.name]: text }))
      }
    } catch (err) {
      setError('Failed to load file preview')
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto py-8">
        <div className="bg-white shadow-md rounded-lg">
          {/* Header */}
          <div className="px-6 py-4 border-b">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold">Final Reports & Chargesheet</h2>
                <p className="text-gray-600 text-sm mt-1">
                  Generated legal documents ready for review and download
                </p>
              </div>
              
              <button
                onClick={loadFinalFiles}
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Refresh Files
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-6">
            {error && (
              <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
                {error}
              </div>
            )}

            {loading ? (
              <div className="text-center py-12">
                <div className="text-gray-500">Loading final files...</div>
              </div>
            ) : finalFiles.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-500 mb-4">
                  No final reports generated yet.
                </div>
                <p className="text-sm text-gray-400">
                  Complete the case diary step to generate final reports and chargesheet.
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                <div className="grid gap-6 md:grid-cols-2">
                  {finalFiles.map((file, index) => (
                    <div key={index} className="border rounded-lg overflow-hidden">
                      <div className="p-4 bg-gray-50 border-b">
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-medium text-gray-900">{file.name}</h3>
                            <div className="text-sm text-gray-500 mt-1">
                              {formatFileSize(file.size)} • {formatDate(file.modified)}
                            </div>
                          </div>
                          
                          <div className="flex space-x-2">
                            {(file.name.endsWith('.txt') || file.name.endsWith('.md')) && (
                              <button
                                onClick={() => handlePreview(file)}
                                className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                              >
                                {previewContent[file.name] ? 'Hide Preview' : 'Preview'}
                              </button>
                            )}
                            
                            <button
                              onClick={() => handleDownload(file)}
                              className="px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
                              title={file.expires_at ? `Link expires at ${new Date(file.expires_at).toLocaleTimeString()}` : 'Download file'}
                            >
                              Download
                            </button>
                          </div>
                        </div>
                      </div>
                      
                      {previewContent[file.name] && (
                        <div className="p-4">
                          <div className="bg-gray-100 rounded-md p-4 max-h-96 overflow-y-auto">
                            <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                              {previewContent[file.name]}
                            </pre>
                          </div>
                          
                          <div className="mt-3 pt-3 border-t">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-500">
                                Preview • {previewContent[file.name].length} characters
                              </span>
                              <button
                                onClick={() => setPreviewContent(prev => ({ ...prev, [file.name]: '' }))}
                                className="text-sm text-indigo-600 hover:text-indigo-800"
                              >
                                Close Preview
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Summary section */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-lg font-medium text-green-800">
                        Case Processing Complete
                      </h3>
                      <div className="mt-2 text-sm text-green-700">
                        <p>
                          All documents have been processed and final reports generated successfully. 
                          You can now download the final report and chargesheet for legal review.
                        </p>
                      </div>
                      <div className="mt-4">
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="font-medium">Final Report:</span> Comprehensive case summary for AI analysis
                          </div>
                          <div>
                            <span className="font-medium">Chargesheet:</span> Legal document ready for court proceedings
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Additional actions */}
                <div className="flex space-x-4 pt-4 border-t">
                  <button
                    onClick={() => window.history.back()}
                    className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                  >
                    ← Back to Case Diary
                  </button>
                  
                  <button
                    onClick={() => window.location.href = '/wizard'}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    Start New Case
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Final