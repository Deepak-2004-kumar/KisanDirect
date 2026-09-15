import React, { useState } from 'react'
import { logisticsApi } from '../services/api'

export default function Logistics() {
  const [form, setForm] = useState({
    farmer_lat: '28.8955', farmer_lon: '76.6066',
    buyer_lat: '28.98', buyer_lon: '76.75', quantity_kg: '500',
  })
  const [plan, setPlan] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const calc = async () => {
    setError(''); setLoading(true)
    try {
      const { data } = await logisticsApi.route({ farmer_lat: Number(form.farmer_lat), farmer_lon: Number(form.farmer_lon), buyer_lat: Number(form.buyer_lat), buyer_lon: Number(form.buyer_lon), quantity_kg: Number(form.quantity_kg) })
      setPlan(data)
    } catch (err) { setError(err.response?.data?.detail || 'Please enter valid coordinates and a quantity greater than zero.') }
    finally { setLoading(false) }
  }

  return (
    <main className="max-w-5xl mx-auto px-4 py-8 space-y-6">
      <header><p className="section-kicker">Delivery decision tool</p><h1 className="text-3xl font-bold text-gray-900">Logistics Planner</h1><p className="text-gray-600 mt-1">Estimate transport cost and delivery feasibility before accepting an offer.</p></header>
      <div className="card">
        <div className="flex items-center justify-between mb-4"><h2 className="text-xl font-bold">Route details</h2><span className="text-xs bg-amber-50 text-amber-700 px-3 py-1 rounded-full">Road-distance estimate</span></div>
        <div className="grid grid-cols-2 gap-3 mb-3">
          <input className="input-field" placeholder="Farmer Lat" value={form.farmer_lat} onChange={(e) => setForm({ ...form, farmer_lat: e.target.value })} />
          <input className="input-field" placeholder="Farmer Lon" value={form.farmer_lon} onChange={(e) => setForm({ ...form, farmer_lon: e.target.value })} />
          <input className="input-field" placeholder="Buyer Lat" value={form.buyer_lat} onChange={(e) => setForm({ ...form, buyer_lat: e.target.value })} />
          <input className="input-field" placeholder="Buyer Lon" value={form.buyer_lon} onChange={(e) => setForm({ ...form, buyer_lon: e.target.value })} />
        </div>
        <input className="input-field mb-3" type="number" placeholder="Quantity (kg)" value={form.quantity_kg} onChange={(e) => setForm({ ...form, quantity_kg: e.target.value })} />
        <button className="btn-primary w-full" onClick={calc} disabled={loading}>{loading ? 'Calculating…' : 'Estimate route'}</button>
      </div>
      {error && <p className="rounded-xl bg-red-50 p-4 text-red-700">{error}</p>}

      {plan && (
        <><section className="grid sm:grid-cols-3 gap-4"><div className="metric-card"><p className="text-xs text-gray-500">Estimated distance</p><p className="text-3xl font-bold text-leaf-800">{plan.distance_km}<span className="text-sm font-normal"> km</span></p></div><div className="metric-card"><p className="text-xs text-gray-500">Transport cost</p><p className="text-3xl font-bold text-leaf-800">₹{plan.estimated_cost}</p></div><div className="metric-card"><p className="text-xs text-gray-500">Delivery time</p><p className="text-3xl font-bold text-leaf-800">{plan.estimated_delivery_hours}<span className="text-sm font-normal"> hrs</span></p></div></section><div className="card"><p className="section-kicker">Recommended plan</p><h2 className="font-semibold text-xl mt-1">{plan.suggested_vehicle}</h2><p className={`mt-3 inline-block rounded-lg px-3 py-2 text-sm font-medium ${plan.estimated_delivery_date_note.includes('MISS') ? 'bg-red-50 text-red-700' : 'bg-leaf-50 text-leaf-800'}`}>{plan.estimated_delivery_date_note}</p><p className="text-xs text-gray-400 mt-5">{plan.scalability_note}</p></div></>
      )}
    </main>
  )
}
