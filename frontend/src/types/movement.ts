export enum OperationType {
  RETURN_PICKUP = 'RETURN_PICKUP',
  RETURN_DEFECT = 'RETURN_DEFECT',
  SELF_PURCHASE = 'SELF_PURCHASE',
  SHIPMENT_RC = 'SHIPMENT_RC',
  UTILIZATION = 'UTILIZATION',
}

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
