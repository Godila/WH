import { OperationType } from '@/types/movement'

export const OPERATION_CONFIG: Record<
  OperationType,
  { sourceRequired: boolean; dcRequired: boolean }
> = {
  [OperationType.RECEIPT]: { sourceRequired: false, dcRequired: false },
  [OperationType.RECEIPT_DEFECT]: { sourceRequired: false, dcRequired: false },
  [OperationType.SHIPMENT_RC]: { sourceRequired: false, dcRequired: true },
  [OperationType.RETURN_PICKUP]: { sourceRequired: true, dcRequired: false },
  [OperationType.RETURN_DEFECT]: { sourceRequired: true, dcRequired: false },
  [OperationType.SELF_PURCHASE]: { sourceRequired: true, dcRequired: false },
  [OperationType.WRITE_OFF]: { sourceRequired: false, dcRequired: false },
  [OperationType.RESTORATION]: { sourceRequired: false, dcRequired: false },
  [OperationType.UTILIZATION]: { sourceRequired: false, dcRequired: false },
}

export const OPERATION_LABELS: Record<OperationType, string> = {
  [OperationType.RECEIPT]: 'Приёмка',
  [OperationType.RECEIPT_DEFECT]: 'Приёмка брака',
  [OperationType.SHIPMENT_RC]: 'Отгрузка в РЦ',
  [OperationType.RETURN_PICKUP]: 'Возврат с ПВЗ',
  [OperationType.RETURN_DEFECT]: 'Возврат брака',
  [OperationType.SELF_PURCHASE]: 'Самовыкуп',
  [OperationType.WRITE_OFF]: 'Списание в брак',
  [OperationType.RESTORATION]: 'Восстановление',
  [OperationType.UTILIZATION]: 'Утилизация',
}
