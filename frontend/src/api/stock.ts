import api from '@/api/client'
import type { StockSummary } from '@/types/stock'

export async function getStockSummary(): Promise<StockSummary> {
  const response = await api.get<StockSummary>('/api/stock/summary')
  return response.data
}
