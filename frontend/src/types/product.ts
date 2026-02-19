export interface Product {
  id: number
  barcode: string
  gtin: string | null
  seller_sku: string | null
  size: string | null
  brand: string | null
  color: string | null
  is_active: boolean
  created_at: string
}

export interface ProductWithStock extends Product {
  stock: number
  defect_stock: number
}
