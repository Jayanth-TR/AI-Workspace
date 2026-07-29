import { Navigate, Route, Routes } from 'react-router-dom'
import ProtectedRoute from './ProtectedRoute'
import MainLayout from '../components/layout/MainLayout'
import Login from '../pages/Login'
import Register from '../pages/Register'
import Dashboard from '../pages/Dashboard'
import Chat from '../pages/Chat'
import Files from '../pages/Files'
import Profile from '../pages/Profile'
import Settings from '../pages/Settings'
import KnowledgeAssistant from '../pages/KnowledgeAssistant'
import ErrorBoundary from '../components/common/ErrorBoundary'

const Secure = ({ children }) => <ProtectedRoute><MainLayout>{children}</MainLayout></ProtectedRoute>

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<Secure><Dashboard /></Secure>} />
      <Route path="/chat" element={<Secure><ErrorBoundary><Chat /></ErrorBoundary></Secure>} />
      <Route path="/files" element={<Secure><Files /></Secure>} />
      <Route path="/profile" element={<Secure><Profile /></Secure>} />
      <Route path="/settings" element={<Secure><Settings /></Secure>} />
      <Route path="/knowledge" element={<Secure><ErrorBoundary><KnowledgeAssistant /></ErrorBoundary></Secure>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
