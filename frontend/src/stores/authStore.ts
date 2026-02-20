import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import api from '@/api/client'
import type { User } from '@/types/user'

interface AuthState {
  token: string | null
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true })
        try {
          const response = await api.post<{ access_token: string }>('/auth/login', {
            email,
            password,
          })

          const token = response.data.access_token
          localStorage.setItem('auth-token', token)
          set({ token })

          await get().fetchUser()
        } finally {
          set({ isLoading: false })
        }
      },

      logout: () => {
        localStorage.removeItem('auth-token')
        localStorage.removeItem('auth-user')
        set({ token: null, user: null })
      },

      fetchUser: async () => {
        try {
          const response = await api.get<User>('/auth/me')
          set({ user: response.data })
        } catch {
          get().logout()
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ token: state.token }),
    }
  )
)
