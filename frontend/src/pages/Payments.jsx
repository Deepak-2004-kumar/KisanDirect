import React, { useState, useEffect } from 'react'
import { ordersApi } from '../services/api'

export default function Payments() {
  const [orders, setOrders] = useState([])
  const load = () => ordersApi.list().then(({ data }) => setOrders(data)).catch(() => {})
  useEffect(() => { load() }, [])

  const pay = async (id) => { await ordersApi.pay(id); load() }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Payments</h1>
      <div className="space-y-3">
        {orders.map((o) => (
          <div key={o.id} className="card flex justify-between items-center">
            <div>
              <p className="font-semibold">Order #{o.id}</p>
              <p className="text-sm text-gray-500">Amount: ₹{o.total_value}</p>
            </div>
            <div className="flex items-center gap-3">
              <span className={`text-xs px-3 py-1 rounded-full font-medium ${o.payment_status === 'PAID' ? 'bg-leaf-100 text-leaf-700' : 'bg-amber-100 text-amber-700'}`}>
                {o.payment_status}
              </span>
              {o.payment_status !== 'PAID' && (
                <button onClick={() => pay(o.id)} className="btn-secondary !py-1.5 !px-4">Mark Paid</button>
              )}
            </div>
          </div>
        ))}
        {orders.length === 0 && <p className="text-gray-400">No payments to show.</p>}
      </div>
    </div>
  )
}
