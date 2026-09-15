import React, { useEffect, useState } from 'react'
import { demandApi } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'

const LEVEL_COLOR = { LOW: 'text-amber-600 bg-amber-50', MEDIUM: 'text-leaf-700 bg-leaf-50', HIGH: 'text-red-600 bg-red-50' }
const crops = ['Tomato', 'Onion', 'Wheat']

export default function DemandForecast() {
  const [crop, setCrop] = useState('Tomato')
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  const [region, setRegion] = useState('')
  const [loading, setLoading] = useState(false)

  const fetchReport = async () => {
    setLoading(true); setError('')
    try {
      const { data } = await demandApi.forecast(crop, region || undefined)
      setReport(data)
    } catch (err) { setError('Demand data could not be loaded for this crop and region.') }
    finally { setLoading(false) }
  }
  useEffect(() => { fetchReport() }, [])

  return (
    <main className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <header><p className="section-kicker">Procurement planning</p><h1 className="text-3xl font-bold text-gray-900">Demand Forecast</h1><p className="text-gray-600 mt-1">Plan harvest, inventory and buyer outreach using expected order demand.</p></header>
      <div className="card">
        <div className="grid sm:grid-cols-[1fr_1fr_auto] gap-3">
          <select className="input-field !py-2 !text-base" value={crop} onChange={(e) => setCrop(e.target.value)}>{crops.map(x => <option key={x}>{x}</option>)}</select>
          <input className="input-field !py-2 !text-base" value={region} onChange={(e) => setRegion(e.target.value)} placeholder="Region (optional)" />
          <button className="btn-primary !py-2 !text-base" onClick={fetchReport} disabled={loading}>{loading ? 'Updating…' : 'Build forecast'}</button>
        </div>
      </div>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {report && (
        <>
          <div className="grid md:grid-cols-3 gap-4"><div className={`card !p-4 ${LEVEL_COLOR[report.demand_level]}`}><p className="text-sm">Demand signal</p><p className="text-3xl font-bold">{report.demand_level}</p><p className="text-sm mt-1">Based on recent order volume</p></div><div className="metric-card"><p className="text-xs text-gray-500">Expected daily demand</p><p className="text-3xl font-bold text-leaf-800 mt-1">{report.expected_daily_quantity_kg}<span className="text-sm font-normal"> kg</span></p></div><div className="metric-card"><p className="text-xs text-gray-500">30-day daily average</p><p className="text-3xl font-bold text-leaf-800 mt-1">{report.trend_30d_avg_kg}<span className="text-sm font-normal"> kg</span></p></div></div>

          <div className="grid lg:grid-cols-3 gap-6"><div className="card lg:col-span-2">
            <h2 className="font-semibold mb-3">7-Day Demand Projection</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={report.trend_7d}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="projected_quantity_kg" fill="#5da838" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <p className="text-xs text-gray-400 mt-2">{report.disclaimer}</p>
          </div><aside className="card"><p className="section-kicker">Planning cue</p><h2 className="font-semibold text-lg mt-1">{report.demand_level === 'HIGH' ? 'Prepare sellable stock' : 'Keep inventory flexible'}</h2><p className="text-sm text-gray-600 leading-6 mt-3">{report.demand_level === 'HIGH' ? 'Confirm harvest readiness and notify repeat buyers early. Consider grouping nearby deliveries to protect margin.' : 'Avoid overcommitting volume. Test buyer demand with smaller lots and compare price intelligence before listing.'}</p></aside></div>
        </>
      )}
    </main>
  )
}
