import api from '@/api/client'
import type { MovementCreate, MovementResponse } from '@/types/movement'

export async function createMovement(data: MovementCreate): Promise<MovementResponse> {
  const response = await api.post<MovementResponse>('/api/stock/movements', data)
  return response.data
}
