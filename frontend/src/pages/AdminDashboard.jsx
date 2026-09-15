import React, { useState, useEffect } from 'react'
import { adminApi } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

export default function AdminDashboard() {
  const [stats, setStats] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    adminApi.analytics().then(({ data }) => setStats(data))
      .catch(() => setError('Could not load analytics — log in as an admin and ensure the backend is running.'))
  }, [])

  const kpis = stats ? [
    ['Total Farmers', stats.total_farmers], ['Total Buyers', stats.total_buyers],
    ['Active Listings', stats.active_listings], ['Active Orders', stats.active_orders],
    ['Total Txn Value (₹)', stats.total_transaction_value], ['Avg Farmer Price (₹/kg)', stats.average_farmer_price],
  ] : []

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-2">Admin Dashboard</h1>
      <p className="text-sm text-gray-400 mb-6">
        Metrics labeled Estimated/Synthetic reflect this prototype's demo data — not verified real-world savings.
      </p>
      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
      {stats && (
        <>
          <div className="grid sm:grid-cols-3 md:grid-cols-6 gap-3 mb-8">
            {kpis.map(([label, val]) => (
              <div key={label} className="card !p-4 text-center">
                <p className="text-xs text-gray-400">{label}</p>
                <p className="text-xl font-bold text-leaf-700">{val}</p>
              </div>
            ))}
          </div>
          <div className="card !p-4 mb-6 bg-amber-50 border-amber-100">
            <p className="text-sm text-amber-800">
              <strong>Estimated Intermediary Layers Reduced:</strong> {stats.estimated_intermediary_layers_reduced}
            </p>
          </div>
          <div className="card">
            <h2 className="font-semibold mb-3">Platform Snapshot</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={[
                { name: 'Farmers', value: stats.total_farmers },
                { name: 'Buyers', value: stats.total_buyers },
                { name: 'Listings', value: stats.active_listings },
                { name: 'Orders', value: stats.active_orders },
              ]}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#4a8a2c" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  )
}
