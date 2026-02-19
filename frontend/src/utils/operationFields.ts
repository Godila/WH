import { OperationType } from '@/types/movement'

export const OPERATION_CONFIG: Record<
  OperationType,
  { sourceRequired: boolean; dcRequired: boolean }
> = {
  [OperationType.RETURN_PICKUP]: { sourceRequired: true, dcRequired: false },
  [OperationType.RETURN_DEFECT]: { sourceRequired: true, dcRequired: false },
  [OperationType.SELF_PURCHASE]: { sourceRequired: true, dcRequired: false },
  [OperationType.SHIPMENT_RC]: { sourceRequired: false, dcRequired: true },
  [OperationType.UTILIZATION]: { sourceRequired: false, dcRequired: false },
}

export const OPERATION_LABELS: Record<OperationType, string> = {
  [OperationType.RETURN_PICKUP]: 'Возврат с ПВЗ',
  [OperationType.RETURN_DEFECT]: 'Возврат брака',
  [OperationType.SELF_PURCHASE]: 'Самовыкуп',
  [OperationType.SHIPMENT_RC]: 'Поставка с РЦ',
  [OperationType.UTILIZATION]: 'Утилизация',
}
