import { useState } from 'react'
import { Modal, Form, InputNumber, Select, message } from 'antd'
import { OperationType, type MovementCreate } from '@/types/movement'
import { OPERATION_CONFIG, OPERATION_LABELS } from '@/utils/operationFields'
import { createMovement } from '@/api/movements'
import ProductSelect from '@/components/products/ProductSelect'
import SourceSelect from '@/components/common/SourceSelect'
import DCSelect from '@/components/common/DCSelect'

interface OperationFormProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

export default function OperationForm({ open, onClose, onSuccess }: OperationFormProps) {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const operationType = Form.useWatch('operation_type', form) as OperationType | undefined

  const config = operationType ? OPERATION_CONFIG[operationType] : null

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      setLoading(true)
      await createMovement({
        operation_type: values.operation_type,
        product_id: values.product_id,
        quantity: values.quantity,
        source_id: values.source_id,
        distribution_center_id: values.distribution_center_id,
      } as MovementCreate)
      message.success('Операция успешно проведена')
      form.resetFields()
      onSuccess()
      onClose()
    } catch (error) {
      console.error('Failed to create movement:', error)
      message.error('Ошибка при проведении операции')
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    form.resetFields()
    onClose()
  }

  return (
    <Modal
      title="Провести операцию"
      open={open}
      onOk={handleSubmit}
      onCancel={handleClose}
      confirmLoading={loading}
      okText="Провести"
      cancelText="Отмена"
    >
      <Form form={form} layout="vertical">
        <Form.Item
          name="operation_type"
          label="Тип операции"
          rules={[{ required: true, message: 'Выберите тип операции' }]}
        >
          <Select
            placeholder="Выберите тип операции"
            options={Object.values(OperationType).map((type) => ({
              value: type,
              label: OPERATION_LABELS[type],
            }))}
            disabled={loading}
          />
        </Form.Item>

        <Form.Item
          name="product_id"
          label="Товар"
          rules={[{ required: true, message: 'Выберите товар' }]}
        >
          <ProductSelect style={{ width: '100%' }} disabled={loading} />
        </Form.Item>

        <Form.Item
          name="quantity"
          label="Количество"
          rules={[{ required: true, message: 'Введите количество' }]}
        >
          <InputNumber min={1} style={{ width: '100%' }} placeholder="Количество" disabled={loading} />
        </Form.Item>

        {config?.sourceRequired && (
          <Form.Item
            name="source_id"
            label="ПВЗ"
            rules={[{ required: true, message: 'Выберите ПВЗ' }]}
          >
            <SourceSelect style={{ width: '100%' }} disabled={loading} />
          </Form.Item>
        )}

        {config?.dcRequired && (
          <Form.Item
            name="distribution_center_id"
            label="РЦ"
            rules={[{ required: true, message: 'Выберите РЦ' }]}
          >
            <DCSelect style={{ width: '100%' }} disabled={loading} />
          </Form.Item>
        )}
      </Form>
    </Modal>
  )
}
