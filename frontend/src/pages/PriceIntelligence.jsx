import React, { useEffect, useState } from 'react'
import { priceApi } from '../services/api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts'

const crops = ['Tomato', 'Onion', 'Wheat']

export default function PriceIntelligence() {
  const [crop, setCrop] = useState('Tomato')
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const fetchReport = async () => {
    setLoading(true); setError('')
    try {
      const { data } = await priceApi.get(crop)
      setReport(data)
    } catch (err) { setError('Price data could not be loaded. Confirm that the backend is available and try again.') }
    finally { setLoading(false) }
  }
  useEffect(() => { fetchReport() }, [])

  const tone = report?.trend_direction === 'up' ? 'text-leaf-700 bg-leaf-50' : report?.trend_direction === 'down' ? 'text-red-700 bg-red-50' : 'text-amber-700 bg-amber-50'

  return (
    <main className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <header className="rounded-3xl bg-leaf-800 text-white p-6 md:p-8 shadow-lg">
        <p className="section-kicker !text-leaf-200">Market decision desk</p><h1 className="text-3xl font-bold mt-1">Price Intelligence</h1>
        <p className="mt-2 max-w-2xl text-leaf-100">Use recent price movement and a transparent short-term estimate to negotiate with confidence.</p>
        <div className="mt-5 flex flex-col sm:flex-row gap-3 max-w-xl"><select className="input-field !py-2 !text-base text-gray-800" value={crop} onChange={e => setCrop(e.target.value)}>{crops.map(x => <option key={x}>{x}</option>)}</select><button className="btn-primary !bg-white !text-leaf-800 !py-2 !text-base" onClick={fetchReport} disabled={loading}>{loading ? 'Refreshing…' : 'Refresh insight'}</button></div>
      </header>

      {error && <p className="text-red-500 text-sm">{error}</p>}

      {report && (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
            {[
              ['Current', report.current_price], ['Average', report.avg_price],
              ['Min', report.min_price], ['Max', report.max_price],
            ].map(([label, val]) => (
              <div key={label} className="metric-card">
                <p className="text-xs text-gray-400">{label}</p>
                <p className="text-2xl font-bold text-leaf-700">₹{val}<span className="text-xs font-normal text-gray-500">/kg</span></p>
              </div>
            ))}
            <div className={`metric-card ${tone}`}><p className="text-xs opacity-75">30-day movement</p><p className="text-2xl font-bold mt-1">{report.trend_pct_30d > 0 ? '+' : ''}{report.trend_pct_30d}%</p><p className="capitalize text-sm">{report.trend_direction}</p></div>
          </div>

          <div className="grid lg:grid-cols-3 gap-6"><div className="card lg:col-span-2">
            <div className="flex justify-between mb-3"><div><h2 className="font-semibold">7-Day Price Outlook</h2><p className="text-sm text-gray-500">Projected price per kg</p></div><span className="text-xs rounded-full bg-gray-100 px-3 py-1 h-fit">Estimate</span></div>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={report.forecast_7d}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis domain={['auto', 'auto']} />
                <Tooltip />
                <ReferenceLine y={report.avg_price} stroke="#94a3b8" strokeDasharray="4 4" />
                <Line type="monotone" dataKey="projected_price" stroke="#4a8a2c" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
            <p className="text-xs text-gray-400 mt-2">Dashed line: recent average. {report.disclaimer}</p>
          </div><aside className="card border-leaf-100"><p className="section-kicker">Recommendation</p><h2 className="font-semibold text-lg mt-1">What to do now</h2><p className="text-sm text-gray-600 mt-3 leading-6">{report.trend_direction === 'up' ? 'Demand is strengthening. Compare buyer offers against the forecast before committing inventory.' : report.trend_direction === 'down' ? 'Prices are softening. Prioritise nearby buyers and reduce transport cost per kilogram.' : 'Prices are stable. Use quality, reliability and delivery terms to select the best offer.'}</p><div className="mt-5 border-t pt-4 text-sm font-medium">Never compare price alone—include quantity, pickup distance and payment timing.</div></aside></div>
        </>
      )}
    </main>
  )
}
