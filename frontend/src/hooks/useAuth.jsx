import { useState, useEffect, createContext, useContext } from 'react'
import React from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem('kd_user')
    return raw ? JSON.parse(raw) : null
  })

  const login = (tokenResponse) => {
    localStorage.setItem('kd_token', tokenResponse.access_token)
    const u = { userId: tokenResponse.user_id, role: tokenResponse.role, fullName: tokenResponse.full_name }
    localStorage.setItem('kd_user', JSON.stringify(u))
    setUser(u)
  }

  const logout = () => {
    localStorage.removeItem('kd_token')
    localStorage.removeItem('kd_user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
