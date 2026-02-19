import api from '@/api/client'

export interface DistributionCenter {
  id: number
  name: string
}

export async function getDCs(): Promise<DistributionCenter[]> {
  const response = await api.get<DistributionCenter[]>('/api/distribution-centers/')
  return response.data
}
