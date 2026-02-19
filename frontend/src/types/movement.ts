export const OperationType = {
  RETURN_PICKUP: 'RETURN_PICKUP',
  RETURN_DEFECT: 'RETURN_DEFECT',
  SELF_PURCHASE: 'SELF_PURCHASE',
  SHIPMENT_RC: 'SHIPMENT_RC',
  UTILIZATION: 'UTILIZATION',
} as const

export type OperationType = typeof OperationType[keyof typeof OperationType]

export interface MovementCreate {
  operation_type: OperationType
  product_id: number
  quantity: number
  source_id?: number
  distribution_center_id?: number
}

export interface MovementResponse {
  id: number
  operation_type: OperationType
  product_id: number
  quantity: number
  source_id: number | null
  distribution_center_id: number | null
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
  skip: number
  limit: number
}

export interface MovementFilters {
  skip?: number
  limit?: number
  operation_type?: OperationType
  product_id?: number
  date_from?: string
  date_to?: string
  barcode?: string
}
