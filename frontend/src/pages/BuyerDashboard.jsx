import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { listingsApi, offersApi, ordersApi } from '../services/api'

export default function BuyerDashboard() {
  const { t } = useTranslation()
  const [crop, setCrop] = useState('')
  const [results, setResults] = useState([])
  const [orders, setOrders] = useState([])
  const [msg, setMsg] = useState('')

  const search = async () => {
    try {
      const { data } = await listingsApi.search({ crop })
      setResults(data)
    } catch (e) { setResults([]) }
  }

  const loadOrders = async () => {
    try {
      const { data } = await ordersApi.list()
      setOrders(data)
    } catch (e) { setOrders([]) }
  }

  useEffect(() => { search(); loadOrders() }, [])

  const makeOffer = async (listing) => {
    const price = prompt(`Your offer price per kg for ${listing.crop} (farmer expects ₹${listing.expected_price_per_kg}):`, listing.expected_price_per_kg)
    if (!price) return
    try {
      await offersApi.create({
        listing_id: listing.id, offered_price_per_kg: Number(price),
        requested_quantity_kg: listing.quantity_kg, needed_within_days: 5,
      })
      setMsg('Offer sent to farmer!')
    } catch (err) {
      setMsg(err.response?.data?.detail || 'Could not send offer')
    }
  }

  const payOrder = async (id) => {
    try {
      await ordersApi.pay(id)
      setMsg('Payment marked as PAID')
      loadOrders()
    } catch (err) { setMsg('Payment failed') }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      {msg && <p className="bg-leaf-50 text-leaf-700 text-sm rounded-lg p-3">{msg}</p>}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Search Crops</h2>
        <div className="flex gap-3">
          <input className="input-field" placeholder="e.g. Tomato" value={crop} onChange={(e) => setCrop(e.target.value)} />
          <button className="btn-primary" onClick={search}>Search</button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {results.map((l) => (
          <div key={l.id} className="card">
            <div className="flex justify-between mb-1">
              <h3 className="font-semibold text-lg">{l.crop}</h3>
              <span className="text-leaf-700 font-bold">₹{l.expected_price_per_kg}/kg</span>
            </div>
            <p className="text-sm text-gray-500 mb-3">
              {l.quantity_kg}kg · {l.quality_grade} · harvest {l.harvest_date}
            </p>
            <button onClick={() => makeOffer(l)} className="btn-secondary w-full !py-2">{t('makeOffer')}</button>
          </div>
        ))}
        {results.length === 0 && <p className="text-gray-400">No listings found. Try a different crop name, or check the backend is running.</p>}
      </div>

      <div className="card">
        <h2 className="text-xl font-bold mb-4">{t('orders')}</h2>
        {orders.length === 0 && <p className="text-gray-400 text-sm">No orders yet.</p>}
        <div className="space-y-2">
          {orders.map((o) => (
            <div key={o.id} className="flex justify-between items-center border-b border-gray-100 py-2">
              <span>Order #{o.id} — {o.final_quantity_kg}kg @ ₹{o.final_price_per_kg}/kg (₹{o.total_value})</span>
              <div className="flex items-center gap-2">
                <span className={`text-xs px-2 py-1 rounded-full ${o.payment_status === 'PAID' ? 'bg-leaf-100 text-leaf-700' : 'bg-amber-100 text-amber-700'}`}>
                  {o.payment_status}
                </span>
                {o.payment_status !== 'PAID' && (
                  <button onClick={() => payOrder(o.id)} className="text-sm text-leaf-600 font-medium">Pay Now</button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
