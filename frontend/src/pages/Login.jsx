import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { authApi } from '../services/api'
import { useAuth } from '../hooks/useAuth'

export default function Login() {
  const { t } = useTranslation()
  const { login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      const { data } = await authApi.login(form)
      login(data)
      const dest = data.role === 'FARMER' ? '/farmer/dashboard'
        : data.role === 'BUYER' ? '/buyer/dashboard' : '/admin/dashboard'
      navigate(dest)
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Check your backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto px-4 py-16">
      <div className="card">
        <h2 className="text-2xl font-bold mb-6 text-center">{t('login')}</h2>
        {error && <p className="bg-red-50 text-red-600 text-sm rounded-lg p-3 mb-4">{error}</p>}
        <form onSubmit={submit} className="space-y-4">
          <input className="input-field" type="email" placeholder="Email" required
                 value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="input-field" type="password" placeholder="Password" required
                 value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          <button className="btn-primary w-full" disabled={loading}>{loading ? '...' : t('login')}</button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-4">
          Demo: farmer1@kisandirect.in / farmer123 · buyer1@kisandirect.in / buyer123
        </p>
        <p className="text-center text-sm mt-2">
          No account? <Link to="/register" className="text-leaf-600 font-medium">{t('register')}</Link>
        </p>
      </div>
    </div>
  )
}
