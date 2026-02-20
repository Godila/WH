export const OperationType = {
  RECEIPT: 'receipt',
  RECEIPT_DEFECT: 'receipt_defect',
  SHIPMENT_RC: 'shipment_rc',
  RETURN_PICKUP: 'return_pickup',
  RETURN_DEFECT: 'return_defect',
  SELF_PURCHASE: 'self_purchase',
  WRITE_OFF: 'write_off',
  RESTORATION: 'restoration',
  UTILIZATION: 'utilization',
} as const

export type OperationType = typeof OperationType[keyof typeof OperationType]

export interface MovementCreate {
  operation_type: OperationType
  product_id: string
  quantity: number
  source_id?: string
  distribution_center_id?: string
}

export interface MovementResponse {
  id: string
  operation_type: OperationType
  product_id: string
  quantity: number
  source_id: string | null
  distribution_center_id: string | null
  created_at: string
}

export interface Movement extends MovementResponse {
  product_barcode?: string
  product_brand?: string
  product_size?: string
  source_name?: string
  dc_name?: string
}

export interface MovementsResponse {
  items: Movement[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface MovementFilters {
  page?: number
  page_size?: number
  operation_type?: OperationType
  product_id?: string
  date_from?: string
  date_to?: string
  barcode?: string
}
