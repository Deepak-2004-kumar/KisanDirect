import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { authApi } from '../services/api'
import { useAuth } from '../hooks/useAuth'

const BUYER_TYPES = ['RETAILER', 'RESTAURANT', 'FOOD_PROCESSOR', 'INSTITUTIONAL', 'FPO_AGGREGATOR']

export default function Register() {
  const { t } = useTranslation()
  const { login } = useAuth()
  const navigate = useNavigate()
  const [role, setRole] = useState('FARMER')
  const [form, setForm] = useState({
    full_name: '', email: '', phone: '', password: '',
    village: '', land_size_acres: '', latitude: '', longitude: '',
    business_name: '', buyer_type: 'RETAILER',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      const payload = { ...form, role, preferred_language: 'en' }
      const { data } = await authApi.register(payload)
      login(data)
      navigate(role === 'FARMER' ? '/farmer/dashboard' : '/buyer/dashboard')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Check your backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-12">
      <div className="card">
        <h2 className="text-2xl font-bold mb-4 text-center">{t('register')}</h2>
        <div className="flex gap-2 mb-6">
          {['FARMER', 'BUYER'].map((r) => (
            <button key={r} type="button" onClick={() => setRole(r)}
              className={`flex-1 py-2 rounded-xl font-medium ${role === r ? 'bg-leaf-600 text-white' : 'bg-gray-100 text-gray-600'}`}>
              {t(r.toLowerCase())}
            </button>
          ))}
        </div>
        {error && <p className="bg-red-50 text-red-600 text-sm rounded-lg p-3 mb-4">{error}</p>}
        <form onSubmit={submit} className="space-y-3">
          <input className="input-field" placeholder="Full Name" required
                 value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          <input className="input-field" type="email" placeholder="Email" required
                 value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="input-field" placeholder="Phone" required
                 value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          <input className="input-field" type="password" placeholder="Password (min 6 chars)" required
                 value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />

          {role === 'FARMER' ? (
            <>
              <input className="input-field" placeholder="Village / Town" required
                     value={form.village} onChange={(e) => setForm({ ...form, village: e.target.value })} />
              <input className="input-field" type="number" step="0.1" placeholder="Land size (acres)"
                     value={form.land_size_acres} onChange={(e) => setForm({ ...form, land_size_acres: e.target.value })} />
            </>
          ) : (
            <>
              <input className="input-field" placeholder="Business name" required
                     value={form.business_name} onChange={(e) => setForm({ ...form, business_name: e.target.value })} />
              <select className="input-field" value={form.buyer_type}
                      onChange={(e) => setForm({ ...form, buyer_type: e.target.value })}>
                {BUYER_TYPES.map((bt) => <option key={bt} value={bt}>{bt.replace('_', ' ')}</option>)}
              </select>
            </>
          )}
          <div className="grid grid-cols-2 gap-3">
            <input className="input-field" type="number" step="0.0001" placeholder="Latitude" required
                   value={form.latitude} onChange={(e) => setForm({ ...form, latitude: e.target.value })} />
            <input className="input-field" type="number" step="0.0001" placeholder="Longitude" required
                   value={form.longitude} onChange={(e) => setForm({ ...form, longitude: e.target.value })} />
          </div>
          <button className="btn-primary w-full" disabled={loading}>{loading ? '...' : t('register')}</button>
        </form>
        <p className="text-center text-sm mt-4">
          Already have an account? <Link to="/login" className="text-leaf-600 font-medium">{t('login')}</Link>
        </p>
      </div>
    </div>
  )
}
