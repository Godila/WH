import api from '@/api/client'

export interface Source {
  id: string
  name: string
}

export async function getSources(): Promise<Source[]> {
  const response = await api.get<Source[]>('/api/sources/')
  return response.data
}
