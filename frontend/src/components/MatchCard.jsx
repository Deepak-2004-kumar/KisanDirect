import React from 'react'

/** Renders an explainable AI match result: score, reasons, warnings. */
export default function MatchCard({ result, buyerName }) {
  if (!result) return null
  const scoreColor = result.match_score >= 85 ? 'text-leaf-600'
    : result.match_score >= 60 ? 'text-wheat-600' : 'text-red-500'

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-2">
        <h4 className="font-semibold text-lg">{buyerName || 'Buyer'}</h4>
        <span className={`text-2xl font-bold ${scoreColor}`}>{Math.round(result.match_score)}%</span>
      </div>
      <p className="text-sm text-gray-500 mb-3">
        Distance: {result.distance_km} km · Est. transport: ₹{result.estimated_transport_cost} ·
        Effective price: ₹{result.effective_price_per_kg}/kg
      </p>
      <ul className="text-sm space-y-1 mb-2">
        {result.reasons?.slice(0, 4).map((r, i) => (
          <li key={i} className="flex gap-2"><span className="text-leaf-600">✓</span>{r}</li>
        ))}
      </ul>
      {result.warnings?.length > 0 && (
        <div className="mt-2 text-sm text-amber-700 bg-amber-50 rounded-lg p-2">
          {result.warnings.map((w, i) => <p key={i}>⚠ {w}</p>)}
        </div>
      )}
    </div>
  )
}
