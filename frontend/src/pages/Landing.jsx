import React from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function Landing() {
  const { t } = useTranslation()
  return (
    <div>
      <section className="max-w-6xl mx-auto px-4 py-16 text-center">
        <h1 className="text-4xl md:text-5xl font-bold text-leaf-800 mb-4">{t('appName')}</h1>
        <p className="text-xl text-gray-600 mb-8">{t('tagline')}</p>
        <p className="max-w-2xl mx-auto text-gray-500 mb-10">
          An AI-powered marketplace connecting farmers directly with retailers, restaurants,
          food processors and institutional buyers — cutting unnecessary middlemen while keeping
          essential logistics, storage and aggregation services transparent and efficient.
        </p>
        <div className="flex justify-center gap-4 flex-wrap">
          <Link to="/register" className="btn-primary">{t('farmer')} — {t('register')}</Link>
          <Link to="/register" className="btn-secondary">{t('buyer')} — {t('register')}</Link>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 py-10 grid md:grid-cols-3 gap-6">
        {[
          { icon: '🤝', title: 'Explainable AI Matching', desc: 'Every recommendation shows exactly why — crop fit, price, distance, and more. Never just the highest bidder.' },
          { icon: '📈', title: 'Price Transparency', desc: 'See market trends, min/max/average prices and short-term forecasts before you decide.' },
          { icon: '🚚', title: 'Smart Logistics', desc: 'Instant distance, transport cost and delivery time estimates for every deal.' },
        ].map((f) => (
          <div key={f.title} className="card text-center">
            <div className="text-4xl mb-3">{f.icon}</div>
            <h3 className="font-semibold text-lg mb-2">{f.title}</h3>
            <p className="text-gray-500 text-sm">{f.desc}</p>
          </div>
        ))}
      </section>
    </div>
  )
}
