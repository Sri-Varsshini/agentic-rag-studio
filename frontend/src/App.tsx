import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Chat from './pages/Chat'
import Ingestion from './pages/Ingestion'
import ProtectedRoute from './components/ProtectedRoute'
import Nav from './components/Nav'

function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <div className="flex flex-col h-screen">
        <Nav />
        <div className="flex-1 overflow-hidden">{children}</div>
      </div>
    </ProtectedRoute>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/chat" element={<AuthLayout><Chat /></AuthLayout>} />
        <Route path="/documents" element={<AuthLayout><Ingestion /></AuthLayout>} />
        <Route path="/" element={<Navigate to="/chat" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
