import { useState, useEffect, useCallback } from 'react'
import { Card, Table, Select, DatePicker, Input, Space, Button, Tag, Spin } from 'antd'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import { getMovements } from '@/api/movements'
import { OperationType, type Movement, type MovementFilters } from '@/types/movement'
import { getMovementColor } from '@/utils/colors'
import { OPERATION_LABELS } from '@/utils/operationFields'

const { RangePicker } = DatePicker

const columns: ColumnsType<Movement> = [
  {
    title: 'Дата',
    dataIndex: 'created_at',
    key: 'created_at',
    width: 180,
    render: (val: string) => dayjs(val).format('DD.MM.YYYY HH:mm'),
  },
  {
    title: 'Тип операции',
    dataIndex: 'operation_type',
    key: 'operation_type',
    width: 150,
    render: (type: OperationType) => (
      <Tag color={getMovementColor(type)}>{OPERATION_LABELS[type]}</Tag>
    ),
  },
  {
    title: 'Товар',
    key: 'product',
    width: 250,
    render: (_, record) => (
      <Space direction="vertical" size={0}>
        <span>{record.product_barcode || `ID: ${record.product_id}`}</span>
        {record.product_brand && (
          <span style={{ color: '#8c8c8c', fontSize: 12 }}>
            {record.product_brand} {record.product_size || ''}
          </span>
        )}
      </Space>
    ),
  },
  {
    title: 'Количество',
    dataIndex: 'quantity',
    key: 'quantity',
    width: 100,
    align: 'right',
  },
  {
    title: 'Источник',
    dataIndex: 'source_name',
    key: 'source_name',
    width: 150,
    render: (val: string | null) => val || '-',
  },
  {
    title: 'РЦ',
    dataIndex: 'dc_name',
    key: 'dc_name',
    width: 150,
    render: (val: string | null) => val || '-',
  },
]

export default function Journal() {
  const [data, setData] = useState<Movement[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 })
  
  const [filters, setFilters] = useState<MovementFilters>({})
  const [operationType, setOperationType] = useState<OperationType | undefined>()
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null] | null>(null)
  const [barcodeSearch, setBarcodeSearch] = useState('')

  const fetchData = useCallback(async () => {
    setLoading(true)
    try {
      const params: MovementFilters = {
        page: pagination.current,
        page_size: pagination.pageSize,
        ...filters,
      }
      const response = await getMovements(params)
      setData(response.items)
      setTotal(response.total)
    } catch (error) {
      console.error('Failed to fetch movements:', error)
    } finally {
      setLoading(false)
    }
  }, [pagination, filters])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleApplyFilters = () => {
    const newFilters: MovementFilters = {}
    
    if (operationType) newFilters.operation_type = operationType
    if (dateRange && dateRange[0] && dateRange[1]) {
      newFilters.date_from = dateRange[0].format('YYYY-MM-DD')
      newFilters.date_to = dateRange[1].format('YYYY-MM-DD')
    }
    if (barcodeSearch.trim()) newFilters.barcode = barcodeSearch.trim()
    
    setFilters(newFilters)
    setPagination({ current: 1, pageSize: pagination.pageSize })
  }

  const handleResetFilters = () => {
    setOperationType(undefined)
    setDateRange(null)
    setBarcodeSearch('')
    setFilters({})
    setPagination({ current: 1, pageSize: 20 })
  }

  const handleTableChange = (pag: { current?: number; pageSize?: number }) => {
    setPagination({
      current: pag.current || 1,
      pageSize: pag.pageSize || 20,
    })
  }

  return (
    <Card title="Журнал движений">
      <Space style={{ marginBottom: 16 }} wrap>
        <Select
          placeholder="Тип операции"
          allowClear
          style={{ width: 180 }}
          value={operationType}
          onChange={setOperationType}
          options={Object.entries(OPERATION_LABELS).map(([value, label]) => ({
            value,
            label,
          }))}
        />
        <RangePicker
          value={dateRange}
          onChange={(dates) => setDateRange(dates)}
          format="DD.MM.YYYY"
          placeholder={['Дата от', 'Дата до']}
        />
        <Input
          placeholder="Поиск по штрихкоду"
          prefix={<SearchOutlined />}
          value={barcodeSearch}
          onChange={(e) => setBarcodeSearch(e.target.value)}
          style={{ width: 200 }}
          allowClear
        />
        <Button type="primary" onClick={handleApplyFilters}>
          Применить
        </Button>
        <Button icon={<ReloadOutlined />} onClick={handleResetFilters}>
          Сбросить
        </Button>
      </Space>

      <Spin spinning={loading}>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total,
            showSizeChanger: true,
            showTotal: (total) => `Всего ${total} записей`,
            defaultPageSize: 20,
          }}
          onChange={handleTableChange}
          scroll={{ x: 1000 }}
        />
      </Spin>
    </Card>
  )
}
