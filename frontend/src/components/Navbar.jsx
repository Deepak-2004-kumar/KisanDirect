import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuth } from '../hooks/useAuth.jsx'

export default function Navbar() {
  const { t, i18n } = useTranslation()
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const switchLang = () => {
    const next = i18n.language === 'en' ? 'hi' : 'en'
    i18n.changeLanguage(next)
    localStorage.setItem('kd_lang', next)
  }

  const doLogout = () => {
    logout()
    navigate('/')
  }

  const dashLink = user?.role === 'FARMER' ? '/farmer/dashboard'
    : user?.role === 'BUYER' ? '/buyer/dashboard'
    : user?.role === 'ADMIN' ? '/admin/dashboard' : '/login'

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 text-leaf-700 font-bold text-xl">
          🌾 {t('appName')}
        </Link>
        <div className="flex items-center gap-3 text-sm md:text-base">
          <Link to="/marketplace" className="hover:text-leaf-700 font-medium hidden sm:inline">{t('marketplace')}</Link>
          <Link to="/price-intelligence" className="hover:text-leaf-700 font-medium hidden lg:inline">Prices</Link>
          <Link to="/demand-forecast" className="hover:text-leaf-700 font-medium hidden lg:inline">Demand</Link>
          <Link to="/logistics" className="hover:text-leaf-700 font-medium hidden lg:inline">Logistics</Link>
          <button onClick={switchLang} className="px-3 py-1.5 rounded-lg border border-gray-300 hover:bg-gray-50">
            {i18n.language === 'en' ? 'हिं' : 'EN'}
          </button>
          {user ? (
            <>
              <Link to={dashLink} className="btn-secondary !py-1.5 !px-4 !text-base">{t('dashboard')}</Link>
              <button onClick={doLogout} className="text-gray-500 hover:text-red-600 font-medium">{t('logout')}</button>
            </>
          ) : (
            <>
              <Link to="/login" className="font-medium hover:text-leaf-700">{t('login')}</Link>
              <Link to="/register" className="btn-primary !py-1.5 !px-4 !text-base">{t('register')}</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
