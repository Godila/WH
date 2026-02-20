import api from '@/api/client'
import type { ProductWithStock } from '@/types/product'

interface ProductsResponse {
  items: ProductWithStock[]
  total: number
  page: number
  page_size: number
  pages: number
}

export async function getProducts(
  page = 1,
  pageSize = 20,
  barcode?: string
): Promise<ProductsResponse> {
  const params = new URLSearchParams()
  params.append('page', String(page))
  params.append('page_size', String(pageSize))
  if (barcode) {
    params.append('barcode', barcode)
  }
  const response = await api.get<ProductsResponse>(`/api/products/?${params.toString()}`)
  return response.data
}

export async function searchProducts(query: string): Promise<ProductsResponse> {
  return getProducts(1, 20, query)
}
