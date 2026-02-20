import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { message } from 'antd'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth-token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth-token')
      localStorage.removeItem('auth-user')
      window.location.href = '/login'
      return Promise.reject(error)
    }

    if (error.code === 'ERR_NETWORK' || !error.response) {
      message.error('Ошибка сети')
      return Promise.reject(error)
    }

    if (error.response?.status === 500) {
      const detail = error.response.data?.detail
      message.error(detail || 'Ошибка сервера')
      return Promise.reject(error)
    }

    return Promise.reject(error)
  }
)

export default api
