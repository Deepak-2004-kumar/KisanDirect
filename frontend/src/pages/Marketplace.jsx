import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { listingsApi } from '../services/api'

export default function Marketplace() {
  const [filters, setFilters] = useState({ crop: '', min_price: '', max_price: '', quality_grade: '' })
  const [listings, setListings] = useState([])

  const search = async () => {
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== ''))
    try {
      const { data } = await listingsApi.search(params)
      setListings(data)
    } catch (e) { setListings([]) }
  }

  useEffect(() => { search() }, [])

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Marketplace</h1>
      <div className="card mb-6 grid sm:grid-cols-5 gap-3">
        <input className="input-field" placeholder="Crop" value={filters.crop}
               onChange={(e) => setFilters({ ...filters, crop: e.target.value })} />
        <input className="input-field" type="number" placeholder="Min ₹/kg" value={filters.min_price}
               onChange={(e) => setFilters({ ...filters, min_price: e.target.value })} />
        <input className="input-field" type="number" placeholder="Max ₹/kg" value={filters.max_price}
               onChange={(e) => setFilters({ ...filters, max_price: e.target.value })} />
        <select className="input-field" value={filters.quality_grade}
                onChange={(e) => setFilters({ ...filters, quality_grade: e.target.value })}>
          <option value="">Any Grade</option><option>Grade A</option><option>Grade B</option><option>Grade C</option>
        </select>
        <button className="btn-primary" onClick={search}>Filter</button>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {listings.map((l) => (
          <Link to={`/crop/${l.id}`} key={l.id} className="card hover:shadow-md transition-shadow">
            <div className="flex justify-between mb-1">
              <h3 className="font-semibold text-lg">{l.crop}</h3>
              <span className="text-leaf-700 font-bold">₹{l.expected_price_per_kg}/kg</span>
            </div>
            <p className="text-sm text-gray-500">{l.quantity_kg}kg · {l.quality_grade}</p>
            <p className="text-xs text-gray-400 mt-1">Harvest: {l.harvest_date}</p>
          </Link>
        ))}
        {listings.length === 0 && <p className="text-gray-400">No listings found.</p>}
      </div>
    </div>
  )
}
