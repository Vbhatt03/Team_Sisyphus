import React, { useState, useEffect } from 'react'
import { useAppStore } from '../store'
import { useNavigate } from 'react-router-dom'

const Login: React.FC = () => {
  const [username, setUsername] = useState('demo')
  const [password, setPassword] = useState('demo123')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  
  const login = useAppStore(state => state.login)
  const checkHealth = useAppStore((state: any) => state.checkHealth)
  const autoDetectApi = useAppStore((state: any) => state.autoDetectApi)
  const setApiBase = useAppStore((state: any) => state.setApiBase)
  const getApiBase = useAppStore((state: any) => state.getApiBase)
  const resetApiBase = useAppStore((state: any) => state.resetApiBase)
  // On mount, attempt automatic detection if health fails
  useEffect(() => {
    (async () => {
      const h = await checkHealth()
      if (!h) {
        await autoDetectApi()
      }
    })()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  const [apiBaseInput, setApiBaseInput] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      // Optional connectivity check before attempting login to surface clearer error
      const health = await checkHealth()
      if (!health) {
        setError('Backend not reachable at configured API URL (port 8000).')
        setLoading(false)
        return
      }
      await login(username, password)
      navigate('/wizard')
    } catch (err: any) {
      console.error('Login error:', err)
      if (err?.response) {
        // Backend responded
        const detail = err.response.data?.detail || 'Authentication failed'
        if (err.response.status === 401) {
          setError(detail === 'Incorrect username or password' ? 'Invalid username or password' : detail)
        } else {
          setError(`Server error (${err.response.status}): ${detail}`)
        }
      } else if (err?.request) {
        // No response - likely network / wrong port
        setError('Cannot reach backend. Check that API server is running on port 8000.')
      } else {
        setError(`Unexpected error during login: ${err?.message || 'Unknown error'}`)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative">
      <div className="fixed top-2 right-2 text-xs bg-white/80 backdrop-blur shadow px-3 py-2 rounded border border-gray-200 space-y-1 max-w-xs">
        <div className="font-semibold">Connection Debug</div>
        <div><span className="font-medium">API:</span> {getApiBase && getApiBase()}</div>
        <div className="flex gap-2">
          <button type="button" onClick={() => autoDetectApi()} className="px-2 py-1 bg-indigo-600 text-white rounded">Detect</button>
          <button type="button" onClick={async () => { const h = await checkHealth(); alert(h ? 'Health OK' : 'Health Failed') }} className="px-2 py-1 bg-gray-600 text-white rounded">Ping</button>
        </div>
      </div>
      <div className="caseflow-container max-w-md w-full mx-4">
        <div className="caseflow-header">
          <h2 className="caseflow-title">
            CaseFlow
          </h2>
          <p className="caseflow-subtitle">
            Legal Case Management System
          </p>
        </div>

        <div className="form-container">
          {error && (
            <div className="error-message slide-in">
              {error}
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div className="text-xs text-gray-500 bg-gray-100 p-2 rounded flex flex-col gap-1">
              <div><strong>API Base:</strong> {getApiBase && getApiBase()}</div>
              <div className="flex gap-2 mt-1">
                <input
                  type="text"
                  placeholder="http://localhost:8000"
                  value={apiBaseInput}
                  onChange={(e) => setApiBaseInput(e.target.value)}
                  className="flex-1 border px-2 py-1 rounded text-xs"
                />
                <button type="button" onClick={() => apiBaseInput && setApiBase(apiBaseInput)} className="px-2 py-1 bg-blue-600 text-white text-xs rounded">Set</button>
                <button type="button" onClick={() => autoDetectApi()} className="px-2 py-1 bg-indigo-600 text-white text-xs rounded">Detect</button>
                  <button type="button" onClick={() => resetApiBase()} className="px-2 py-1 bg-gray-500 text-white text-xs rounded">Reset</button>
              </div>
            </div>
            <div className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  className="input-field"
                  placeholder="Enter your username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    className="input-field pr-12"
                    placeholder="Enter your password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(s => !s)}
                    className="absolute inset-y-0 right-0 px-3 flex items-center text-sm text-gray-500 hover:text-gray-700 focus:outline-none"
                    tabIndex={-1}
                  >
                    {showPassword ? 'Hide' : 'Show'}
                  </button>
                </div>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full flex items-center justify-center"
              >
                {loading && <div className="loading-spinner"></div>}
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
            </div>

            <div className="text-center text-sm text-gray-500">
              Demo credentials: <strong>demo</strong> / <strong>demo123</strong>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default Login