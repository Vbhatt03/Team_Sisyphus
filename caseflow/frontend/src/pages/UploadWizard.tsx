import React, { useState, useEffect, useRef } from 'react'
import { useAppStore } from '../store'
import { useNavigate } from 'react-router-dom'

const UploadWizard: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1)
  const [caseName, setCaseName] = useState('')
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState('')

  const {
    uploadStatus,
    uploadLogs,
    createCase,
    uploadFile,
    parseDocuments
  } = useAppStore()

  const navigate = useNavigate()

  const steps = [
    { id: 1, title: 'Create Case', type: 'case' },
    { id: 2, title: 'Upload FIR', type: 'fir', required: true },
    { id: 3, title: 'Upload Victim Medical Report', type: 'victim_med', required: false },
    { id: 4, title: 'Upload Accused Medical Report', type: 'accused_med', required: false },
    { id: 5, title: 'Upload Statement', type: 'statement', required: true },
    { id: 6, title: 'Process Documents', type: 'process' }
  ]

  const currentStepData = steps[currentStep - 1]

  const handleCreateCase = async () => {
    if (!caseName.trim()) {
      setError('Case name is required')
      return
    }
    
    try {
      await createCase(caseName)
      setCurrentStep(2)
      setError('')
    } catch (err) {
      setError('Failed to create case')
    }
  }

  const handleFileUpload = async (file: File | null, skip = false) => {
    if (!file && !skip && currentStepData.required) {
      setError('This file is required')
      return
    }

    try {
      await uploadFile(currentStepData.type, file, skip)
      setCurrentStep(currentStep + 1)
      setError('')
    } catch (err) {
      setError('Upload failed')
    }
  }

  const handleParse = async () => {
    setProcessing(true)
    setError('')

    try {
      await parseDocuments()
      navigate('/compliance')
    } catch (err) {
      setError('Document parsing failed')
    } finally {
      setProcessing(false)
    }
  }

  const renderStep = () => {
    if (currentStep === 1) {
      return (
        <div className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-800 text-center">Create New Case</h3>
          <div className="space-y-4">
            <input
              type="text"
              placeholder="Enter case name"
              value={caseName}
              onChange={(e) => setCaseName(e.target.value)}
              className="input-field"
            />
            <button
              onClick={handleCreateCase}
              className="btn-primary w-full"
            >
              Create Case
            </button>
          </div>
        </div>
      )
    }

    if (currentStep === 6) {
      return (
        <div className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-800 text-center">Process Documents</h3>

          <div className="status-card">
            <h4 className="font-semibold mb-3 text-gray-800">Upload Status:</h4>
            <ul className="space-y-2">
              <li className={`flex items-center space-x-2 ${uploadStatus.fir ? 'text-green-700' : 'text-red-700'}`}>
                <span>{uploadStatus.fir ? '✅' : '❌'}</span>
                <span>FIR Document</span>
              </li>
              <li className={`flex items-center space-x-2 ${uploadStatus.statement ? 'text-green-700' : 'text-red-700'}`}>
                <span>{uploadStatus.statement ? '✅' : '❌'}</span>
                <span>Statement Document</span>
              </li>
              <li className={`flex items-center space-x-2 ${uploadStatus.victim_med === 'skipped' ? 'text-blue-700' : uploadStatus.victim_med ? 'text-green-700' : 'text-red-700'}`}>
                <span>{uploadStatus.victim_med === 'skipped' ? '⏭️' : uploadStatus.victim_med ? '✅' : '❌'}</span>
                <span>Victim Medical Report</span>
              </li>
              <li className={`flex items-center space-x-2 ${uploadStatus.accused_med === 'skipped' ? 'text-blue-700' : uploadStatus.accused_med ? 'text-green-700' : 'text-red-700'}`}>
                <span>{uploadStatus.accused_med === 'skipped' ? '⏭️' : uploadStatus.accused_med ? '✅' : '❌'}</span>
                <span>Accused Medical Report</span>
              </li>
            </ul>
          </div>

          {uploadLogs.length > 0 && (
            <div className="status-card max-h-48 overflow-y-auto">
              <h4 className="font-semibold mb-3 text-gray-800">Processing Logs:</h4>
              {uploadLogs.map((log, index) => (
                <div key={index} className="text-sm text-gray-600 font-mono bg-gray-50 p-2 rounded mb-1">
                  {log}
                </div>
              ))}
            </div>
          )}

          <button
            onClick={handleParse}
            disabled={processing || (!uploadStatus.fir || !uploadStatus.statement)}
            className="btn-primary w-full flex items-center justify-center"
          >
            {processing && <div className="loading-spinner mr-2"></div>}
            {processing ? 'Processing Documents...' : 'Parse Documents'}
          </button>
        </div>
      )
    }

    // File upload steps
    return (
      <FileUploadStep
        key={currentStepData.type} // force remount so internal file state resets per step
        title={currentStepData.title}
        type={currentStepData.type}
        required={currentStepData.required || false}
        onUpload={handleFileUpload}
      />
    )
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-4xl mx-auto py-8">
        <div className="caseflow-container">
          {/* Progress bar */}
          <div className="progress-container">
            <div className="progress-text">
              <h2 className="text-xl font-bold text-gray-800">Upload Wizard</h2>
              <span className="text-sm font-medium text-gray-600">Step {currentStep} of {steps.length}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
              <div
                className="progress-bar"
                style={{ width: `${(currentStep / steps.length) * 100}%` }}
              ></div>
            </div>
          </div>

          {/* Step content */}
          <div className="p-8">
            {error && (
              <div className="error-message mb-6">
                {error}
              </div>
            )}

            {renderStep()}
          </div>

          {/* Navigation */}
          <div className="nav-buttons">
            <button
              onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
              disabled={currentStep === 1}
              className="nav-btn btn-outline"
            >
              Previous
            </button>

            {currentStep < steps.length && currentStep !== 1 && currentStep !== 6 && (
              <button
                onClick={() => setCurrentStep(currentStep + 1)}
                className="nav-btn btn-secondary"
              >
                Skip
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

const FileUploadStep: React.FC<{
  title: string
  type: string
  required: boolean
  onUpload: (file: File | null, skip?: boolean) => Promise<void>
}> = ({ title, type, required, onUpload }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragOver, setDragOver] = useState(false)
  const [error, setError] = useState<string>('')
  const inputRef = useRef<HTMLInputElement | null>(null)

  // Reset selection whenever the step/type changes to avoid carrying previous file forward
  useEffect(() => {
    setSelectedFile(null)
    setError('')
  }, [type])

  const validateFile = (file: File): boolean => {
    // Check file type
    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a valid PDF file.')
      return false
    }

    // Check file size (20MB limit)
    const maxSize = 20 * 1024 * 1024 // 20MB
    if (file.size > maxSize) {
      setError('File size must be less than 20MB.')
      return false
    }

    setError('')
    return true
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && validateFile(file)) {
      setSelectedFile(file)
    } else if (file) {
      // Reset the input if file is invalid
      e.target.value = ''
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file && validateFile(file)) {
      setSelectedFile(file)
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      onUpload(selectedFile)
    }
  }

  const handleSkip = () => {
    onUpload(null, true)
  }

  const clearSelection = () => {
    setSelectedFile(null)
    setError('')
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  const handleAreaClick = () => {
    if (!selectedFile && inputRef.current) {
      inputRef.current.click()
    }
  }

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-gray-800 text-center">{title}</h3>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div
        className={`upload-area ${selectedFile ? 'has-file' : ''} ${dragOver ? 'drag-over' : ''}`}
        onClick={handleAreaClick}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        {selectedFile ? (
          <div className="space-y-3 text-center">
            <div className="text-green-600 font-semibold text-lg">✓ File selected:</div>
            <div className="text-gray-700 font-medium">{selectedFile.name}</div>
            <div className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full inline-block">
              {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
            </div>
            <button
              onClick={clearSelection}
              className="text-sm text-red-600 hover:text-red-800 mt-2 underline"
            >
              Clear selection
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="upload-icon">📄</div>
            <div className="upload-text">Drop PDF file here or click to browse</div>
            <div className="upload-subtext">Only .pdf up to 20MB. You can re-select the same file name.</div>
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf,.pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); inputRef.current?.click() }}
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2"
            >
              Choose PDF
            </button>
          </div>
        )}
      </div>

      <div className="flex space-x-4">
        <button
          onClick={handleUpload}
          disabled={!selectedFile}
          className="btn-primary flex-1 flex items-center justify-center"
        >
          Upload File
        </button>

        {!required && (
          <button
            onClick={handleSkip}
            className="btn-outline"
          >
            Skip
          </button>
        )}
      </div>
    </div>
  )
}

export default UploadWizard