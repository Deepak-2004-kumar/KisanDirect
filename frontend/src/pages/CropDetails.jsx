import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { listingsApi, priceApi, logisticsApi } from '../services/api'

export default function CropDetails() {
  const { id } = useParams()
  const [listing, setListing] = useState(null)
  const [price, setPrice] = useState(null)
  const [route, setRoute] = useState(null)

  useEffect(() => {
    listingsApi.get(id).then(({ data }) => {
      setListing(data)
      priceApi.get(data.crop).then((r) => setPrice(r.data)).catch(() => {})
    }).catch(() => {})
  }, [id])

  const estimateRoute = async () => {
    // demo: estimate to a fixed reference buyer location (Delhi) if user hasn't got one
    const { data } = await logisticsApi.route({
      farmer_lat: listing.latitude, farmer_lon: listing.longitude,
      buyer_lat: 28.7041, buyer_lon: 77.1025, quantity_kg: listing.quantity_kg,
    })
    setRoute(data)
  }

  if (!listing) return <div className="max-w-3xl mx-auto px-4 py-10 text-gray-400">Loading…</div>

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
      <div className="card">
        <h1 className="text-2xl font-bold mb-2">{listing.crop}</h1>
        <p className="text-gray-500 mb-4">{listing.quality_grade} · {listing.quantity_kg}kg · Harvest {listing.harvest_date}</p>
        <p className="text-3xl font-bold text-leaf-700">₹{listing.expected_price_per_kg}/kg</p>
      </div>

      {price && (
        <div className="card">
          <h2 className="font-semibold mb-2">Market Price Context (synthetic demo data)</h2>
          <p className="text-sm text-gray-600">Avg ₹{price.avg_price} · Min ₹{price.min_price} · Max ₹{price.max_price} · Trend: {price.trend_direction}</p>
          <p className="text-xs text-gray-400 mt-2">{price.disclaimer}</p>
        </div>
      )}

      <div className="card">
        <h2 className="font-semibold mb-3">Estimated Logistics to a Sample Buyer</h2>
        <button className="btn-secondary" onClick={estimateRoute}>Estimate Route</button>
        {route && (
          <div className="mt-3 text-sm text-gray-600">
            <p>Distance: {route.distance_km} km · Vehicle: {route.suggested_vehicle}</p>
            <p>Estimated cost: ₹{route.estimated_cost} · Delivery time: {route.estimated_delivery_hours}h</p>
          </div>
        )}
      </div>
    </div>
  )
}
