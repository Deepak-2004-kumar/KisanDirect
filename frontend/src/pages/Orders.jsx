import React, { useState, useEffect } from 'react'
import { ordersApi } from '../services/api'

export default function Orders() {
  const [orders, setOrders] = useState([])
  useEffect(() => { ordersApi.list().then(({ data }) => setOrders(data)).catch(() => {}) }, [])

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Orders</h1>
      <div className="space-y-3">
        {orders.map((o) => (
          <div key={o.id} className="card flex justify-between items-center">
            <div>
              <p className="font-semibold">Order #{o.id}</p>
              <p className="text-sm text-gray-500">{o.final_quantity_kg}kg @ ₹{o.final_price_per_kg}/kg — ₹{o.total_value}</p>
            </div>
            <div className="text-right text-sm">
              <p>Status: <span className="font-medium">{o.status}</span></p>
              <p>Payment: <span className="font-medium">{o.payment_status}</span></p>
            </div>
          </div>
        ))}
        {orders.length === 0 && <p className="text-gray-400">No orders found.</p>}
      </div>
    </div>
  )
}
