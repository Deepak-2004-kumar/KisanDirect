import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './hooks/useAuth'
import Navbar from './components/Navbar'

import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import FarmerDashboard from './pages/FarmerDashboard'
import BuyerDashboard from './pages/BuyerDashboard'
import Marketplace from './pages/Marketplace'
import CropDetails from './pages/CropDetails'
import AIRecommendations from './pages/AIRecommendations'
import PriceIntelligence from './pages/PriceIntelligence'
import DemandForecast from './pages/DemandForecast'
import Logistics from './pages/Logistics'
import Orders from './pages/Orders'
import Payments from './pages/Payments'
import AdminDashboard from './pages/AdminDashboard'

function ProtectedRoute({ children, role }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (role && user.role !== role) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/marketplace" element={<Marketplace />} />
          <Route path="/crop/:id" element={<CropDetails />} />
          <Route path="/ai-recommendations" element={<AIRecommendations />} />
          <Route path="/price-intelligence" element={<PriceIntelligence />} />
          <Route path="/demand-forecast" element={<DemandForecast />} />
          <Route path="/logistics" element={<Logistics />} />
          <Route path="/orders" element={<ProtectedRoute><Orders /></ProtectedRoute>} />
          <Route path="/payments" element={<ProtectedRoute><Payments /></ProtectedRoute>} />
          <Route path="/farmer/dashboard" element={<ProtectedRoute role="FARMER"><FarmerDashboard /></ProtectedRoute>} />
          <Route path="/buyer/dashboard" element={<ProtectedRoute role="BUYER"><BuyerDashboard /></ProtectedRoute>} />
          <Route path="/admin/dashboard" element={<ProtectedRoute role="ADMIN"><AdminDashboard /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
