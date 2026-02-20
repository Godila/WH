import api from '@/api/client'
import type { MovementCreate, MovementResponse, MovementsResponse, MovementFilters } from '@/types/movement'

export async function createMovement(data: MovementCreate): Promise<MovementResponse> {
  const response = await api.post<MovementResponse>('/stock/movements', data)
  return response.data
}

export async function getMovements(filters: MovementFilters = {}): Promise<MovementsResponse> {
  const params = new URLSearchParams()
  
  if (filters.page !== undefined) params.append('page', String(filters.page))
  if (filters.page_size !== undefined) params.append('page_size', String(filters.page_size))
  if (filters.operation_type) params.append('operation_type', filters.operation_type)
  if (filters.product_id !== undefined) params.append('product_id', String(filters.product_id))
  if (filters.date_from) params.append('date_from', filters.date_from)
  if (filters.date_to) params.append('date_to', filters.date_to)
  if (filters.barcode) params.append('barcode', filters.barcode)
  
  const response = await api.get<MovementsResponse>('/stock/movements', { params })
  return response.data
}
