import { useState, useCallback } from 'react'
import { message } from 'antd'
import type { AxiosError } from 'axios'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

interface UseApiReturn<T, P extends unknown[]> extends UseApiState<T> {
  execute: (...params: P) => Promise<T | null>
}

export function useApi<T, P extends unknown[] = []>(
  apiFunction: (...params: P) => Promise<T>
): UseApiReturn<T, P> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  const execute = useCallback(
    async (...params: P): Promise<T | null> => {
      setState((prev) => ({ ...prev, loading: true, error: null }))

      try {
        const result = await apiFunction(...params)
        setState({ data: result, loading: false, error: null })
        return result
      } catch (err) {
        const axiosError = err as AxiosError<{ detail?: string }>
        const errorMessage = 
          axiosError.response?.data?.detail ||
          axiosError.message ||
          'Произошла ошибка'
        
        setState({ data: null, loading: false, error: errorMessage })
        message.error(errorMessage)
        return null
      }
    },
    [apiFunction]
  )

  return {
    ...state,
    execute,
  }
}

export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  
  const axiosError = error as AxiosError<{ detail?: string }>
  if (axiosError.response?.data?.detail) {
    return axiosError.response.data.detail
  }
  
  if (axiosError.message === 'Network Error') {
    return 'Ошибка сети'
  }
  
  if (axiosError.response?.status === 500) {
    return 'Ошибка сервера'
  }
  
  return 'Произошла ошибка'
}
