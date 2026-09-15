import React, { useState } from 'react'
import { aiApi } from '../services/api'
import MatchCard from '../components/MatchCard'

export default function AIRecommendations() {
  const [listingId, setListingId] = useState('')
  const [buyerId, setBuyerId] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const run = async () => {
    setError(''); setResult(null)
    try {
      const { data } = await aiApi.match({ listing_id: Number(listingId), buyer_id: Number(buyerId) })
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not compute match — check IDs and backend.')
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      <div className="card">
        <h1 className="text-xl font-bold mb-4">AI Match Explorer</h1>
        <p className="text-sm text-gray-500 mb-4">
          Enter a crop listing ID and a buyer ID to see the transparent AI match score and reasoning
          used throughout KisanDirect — the same engine used automatically when a buyer makes an offer.
        </p>
        <div className="grid grid-cols-2 gap-3 mb-3">
          <input className="input-field" placeholder="Listing ID" value={listingId} onChange={(e) => setListingId(e.target.value)} />
          <input className="input-field" placeholder="Buyer ID" value={buyerId} onChange={(e) => setBuyerId(e.target.value)} />
        </div>
        <button className="btn-primary w-full" onClick={run}>Compute Match</button>
        {error && <p className="text-red-500 text-sm mt-3">{error}</p>}
      </div>
      {result && <MatchCard result={result} buyerName={`Buyer #${buyerId}`} />}
    </div>
  )
}
