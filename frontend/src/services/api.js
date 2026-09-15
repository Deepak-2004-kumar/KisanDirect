import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('kd_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
}

export const listingsApi = {
  create: (data) => api.post('/crop-listings', data),
  search: (params) => api.get('/crop-listings', { params }),
  get: (id) => api.get(`/crop-listings/${id}`),
  update: (id, data) => api.put(`/crop-listings/${id}`, data),
  remove: (id) => api.delete(`/crop-listings/${id}`),
}

export const offersApi = {
  create: (data) => api.post('/offers', data),
  list: (listingId) => api.get('/offers', { params: { listing_id: listingId } }),
  accept: (id) => api.post(`/offers/${id}/accept`),
}

export const ordersApi = {
  list: () => api.get('/orders'),
  get: (id) => api.get(`/orders/${id}`),
  pay: (id) => api.post(`/orders/${id}/pay`),
}

export const aiApi = {
  match: (data) => api.post('/ai/match', data),
}

export const priceApi = {
  get: (crop) => api.get('/prices', { params: { crop } }),
  trends: (crop) => api.get('/prices/trends', { params: { crop } }),
}

export const demandApi = {
  forecast: (crop, region) => api.get('/demand/forecast', { params: { crop, region } }),
}

export const logisticsApi = {
  route: (data) => api.post('/logistics/route', data),
}

export const adminApi = {
  analytics: () => api.get('/admin/analytics'),
}

export default api
