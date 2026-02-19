import { OperationType } from '@/types/movement'

export const MOVEMENT_COLORS: Record<OperationType, string> = {
  [OperationType.RETURN_PICKUP]: '#52c41a',
  [OperationType.RETURN_DEFECT]: '#fa8c16',
  [OperationType.SELF_PURCHASE]: '#52c41a',
  [OperationType.SHIPMENT_RC]: '#1890ff',
  [OperationType.UTILIZATION]: '#ff4d4f',
}

export function getMovementColor(type: OperationType): string {
  return MOVEMENT_COLORS[type] || '#8c8c8c'
}
