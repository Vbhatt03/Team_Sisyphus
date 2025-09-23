import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAppStore } from './store'
import Login from './pages/Login'
import UploadWizard from './pages/UploadWizard'
import Compliance from './pages/Compliance'
import CaseDiary from './pages/CaseDiary'
import Final from './pages/Final'

function App() {
  const { isAuthenticated } = useAppStore()

  // Check for existing token on app load
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token && !isAuthenticated) {
      // Could validate token here by calling /api/auth/me
    }
  }, [isAuthenticated])

  return (
    <div className="App min-h-screen fade-in">
      <Routes>
        <Route
          path="/login"
          element={isAuthenticated ? <Navigate to="/wizard" /> : <Login />}
        />
        <Route
          path="/wizard"
          element={isAuthenticated ? <UploadWizard /> : <Navigate to="/login" />}
        />
        <Route
          path="/compliance"
          element={isAuthenticated ? <Compliance /> : <Navigate to="/login" />}
        />
        <Route
          path="/case-diary"
          element={isAuthenticated ? <CaseDiary /> : <Navigate to="/login" />}
        />
        <Route
          path="/final"
          element={isAuthenticated ? <Final /> : <Navigate to="/login" />}
        />
        <Route
          path="/"
          element={<Navigate to={isAuthenticated ? "/wizard" : "/login"} />}
        />
      </Routes>
    </div>
  )
}

export default App
