import api from '@/api/client'
import type { ProductWithStock } from '@/types/product'

interface ProductsResponse {
  items: ProductWithStock[]
  total: number
}

export async function getProducts(
  skip = 0,
  limit = 20,
  barcode?: string
): Promise<ProductsResponse> {
  const params = new URLSearchParams()
  params.append('skip', String(skip))
  params.append('limit', String(limit))
  if (barcode) {
    params.append('barcode', barcode)
  }
  const response = await api.get<ProductsResponse>(`/api/products/?${params.toString()}`)
  return response.data
}

export async function searchProducts(query: string): Promise<ProductsResponse> {
  return getProducts(0, 20, query)
}
