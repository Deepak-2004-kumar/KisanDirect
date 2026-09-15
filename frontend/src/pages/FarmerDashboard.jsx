import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { listingsApi, offersApi, priceApi } from '../services/api'
import MatchCard from '../components/MatchCard'

export default function FarmerDashboard() {
  const { t } = useTranslation()
  const [listings, setListings] = useState([])
  const [selectedListing, setSelectedListing] = useState(null)
  const [offers, setOffers] = useState([])
  const [priceHint, setPriceHint] = useState(null)
  const [form, setForm] = useState({
    crop: '', quantity_kg: '', quality_grade: 'Grade A', expected_price_per_kg: '',
    harvest_date: '', latitude: '', longitude: '',
  })
  const [msg, setMsg] = useState('')

  const loadListings = async () => {
    try {
      const { data } = await listingsApi.search({})
      setListings(data)
    } catch (e) { /* backend may not be running in static preview */ }
  }

  useEffect(() => { loadListings() }, [])

  const loadOffers = async (listingId) => {
    setSelectedListing(listingId)
    try {
      const { data } = await offersApi.list(listingId)
      setOffers(data)
    } catch (e) { setOffers([]) }
  }

  const checkPrice = async (crop) => {
    if (!crop) return
    try {
      const { data } = await priceApi.get(crop)
      setPriceHint(data)
    } catch (e) { setPriceHint(null) }
  }

  const submitListing = async (e) => {
    e.preventDefault()
    setMsg('')
    try {
      await listingsApi.create({ ...form, quantity_kg: Number(form.quantity_kg),
        expected_price_per_kg: Number(form.expected_price_per_kg),
        latitude: Number(form.latitude), longitude: Number(form.longitude) })
      setMsg('Listing created!')
      setForm({ crop: '', quantity_kg: '', quality_grade: 'Grade A', expected_price_per_kg: '',
        harvest_date: '', latitude: '', longitude: '' })
      loadListings()
    } catch (err) {
      setMsg(err.response?.data?.detail || 'Could not create listing — is the backend running?')
    }
  }

  const acceptOffer = async (offerId) => {
    try {
      await offersApi.accept(offerId)
      setMsg('Offer accepted — order created!')
      loadOffers(selectedListing)
    } catch (err) {
      setMsg(err.response?.data?.detail || 'Could not accept offer')
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 grid md:grid-cols-2 gap-6">
      <div className="card">
        <h2 className="text-xl font-bold mb-4">{t('addCrop')}</h2>
        {msg && <p className="bg-leaf-50 text-leaf-700 text-sm rounded-lg p-3 mb-3">{msg}</p>}
        <form onSubmit={submitListing} className="space-y-3">
          <input className="input-field" placeholder={t('crop')} required
                 value={form.crop}
                 onChange={(e) => { setForm({ ...form, crop: e.target.value }); checkPrice(e.target.value) }} />
          {priceHint && (
            <p className="text-xs text-gray-500 -mt-2">
              Market avg (synthetic demo data): ₹{priceHint.avg_price}/kg · trend: {priceHint.trend_direction}
            </p>
          )}
          <div className="grid grid-cols-2 gap-3">
            <input className="input-field" type="number" placeholder={t('quantity')} required
                   value={form.quantity_kg} onChange={(e) => setForm({ ...form, quantity_kg: e.target.value })} />
            <select className="input-field" value={form.quality_grade}
                    onChange={(e) => setForm({ ...form, quality_grade: e.target.value })}>
              <option>Grade A</option><option>Grade B</option><option>Grade C</option>
            </select>
          </div>
          <input className="input-field" type="number" step="0.5" placeholder={t('expectedPrice')} required
                 value={form.expected_price_per_kg} onChange={(e) => setForm({ ...form, expected_price_per_kg: e.target.value })} />
          <input className="input-field" type="date" required
                 value={form.harvest_date} onChange={(e) => setForm({ ...form, harvest_date: e.target.value })} />
          <div className="grid grid-cols-2 gap-3">
            <input className="input-field" type="number" step="0.0001" placeholder="Latitude" required
                   value={form.latitude} onChange={(e) => setForm({ ...form, latitude: e.target.value })} />
            <input className="input-field" type="number" step="0.0001" placeholder="Longitude" required
                   value={form.longitude} onChange={(e) => setForm({ ...form, longitude: e.target.value })} />
          </div>
          <button className="btn-primary w-full">{t('submit')}</button>
        </form>
      </div>

      <div className="space-y-4">
        <div className="card">
          <h2 className="text-xl font-bold mb-4">{t('myListings')}</h2>
          <div className="space-y-2 max-h-72 overflow-y-auto">
            {listings.length === 0 && <p className="text-gray-400 text-sm">No listings yet, or backend not connected.</p>}
            {listings.map((l) => (
              <button key={l.id} onClick={() => loadOffers(l.id)}
                className={`w-full text-left p-3 rounded-xl border ${selectedListing === l.id ? 'border-leaf-500 bg-leaf-50' : 'border-gray-200'}`}>
                <div className="flex justify-between">
                  <span className="font-medium">{l.crop} — {l.quantity_kg}kg ({l.quality_grade})</span>
                  <span className="text-leaf-700 font-semibold">₹{l.expected_price_per_kg}/kg</span>
                </div>
                <span className="text-xs text-gray-400">{l.status} · harvest {l.harvest_date}</span>
              </button>
            ))}
          </div>
        </div>

        {selectedListing && (
          <div>
            <h3 className="font-bold mb-2">{t('offers')} & {t('aiRecommendation')}</h3>
            {offers.length === 0 && <p className="text-gray-400 text-sm">No offers yet for this listing.</p>}
            <div className="space-y-3">
              {offers.map((o) => (
                <div key={o.id}>
                  <MatchCard result={o.match_explanation} buyerName={`Buyer #${o.buyer_id} — ₹${o.offered_price_per_kg}/kg`} />
                  {o.status === 'PENDING' && (
                    <button onClick={() => acceptOffer(o.id)} className="btn-primary w-full mt-2 !py-2">
                      {t('acceptOffer')}
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
