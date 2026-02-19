import { Routes, Route, Navigate } from 'react-router-dom'
import Login from '@/pages/Login'
import ProtectedRoute from '@/components/common/ProtectedRoute'

function Dashboard() {
  return <div style={{ padding: 24 }}>Dashboard</div>
}

function Movements() {
  return <div style={{ padding: 24 }}>Movements Journal</div>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/movements"
        element={
          <ProtectedRoute>
            <Movements />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
