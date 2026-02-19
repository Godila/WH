import { Routes, Route, Navigate } from 'react-router-dom'

function Dashboard() {
  return <div>Dashboard</div>
}

function Movements() {
  return <div>Movements Journal</div>
}

function App() {
  return (
    <Routes>
      <Route path="/login" element={<div>Login</div>} />
      <Route path="/" element={<Dashboard />} />
      <Route path="/movements" element={<Movements />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
