import api from '@/api/client'

export interface DistributionCenter {
  id: string
  name: string
}

export async function getDCs(): Promise<DistributionCenter[]> {
  const response = await api.get<DistributionCenter[]>('/distribution-centers/')
  return response.data
}
