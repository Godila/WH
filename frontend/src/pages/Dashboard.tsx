import { useState, useEffect, useCallback } from 'react'
import { Card, Col, Row, Statistic, Table, Input, Space, Spin, Button } from 'antd'
import { PackageOutlined, InboxOutlined, WarningOutlined, PlusOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { getProducts, searchProducts } from '@/api/products'
import { getStockSummary } from '@/api/stock'
import type { ProductWithStock } from '@/types/product'
import type { StockSummary } from '@/types/stock'
import OperationForm from '@/pages/Movements/OperationForm'

const columns: ColumnsType<ProductWithStock> = [
  {
    title: 'Штрихкод',
    dataIndex: 'barcode',
    key: 'barcode',
    width: 150,
  },
  {
    title: 'GTIN',
    dataIndex: 'gtin',
    key: 'gtin',
    width: 150,
    render: (val: string | null) => val || '-',
  },
  {
    title: 'SKU продавца',
    dataIndex: 'seller_sku',
    key: 'seller_sku',
    width: 150,
    render: (val: string | null) => val || '-',
  },
  {
    title: 'Бренд',
    dataIndex: 'brand',
    key: 'brand',
    width: 150,
    render: (val: string | null) => val || '-',
  },
  {
    title: 'Размер',
    dataIndex: 'size',
    key: 'size',
    width: 100,
    render: (val: string | null) => val || '-',
  },
  {
    title: 'Остаток',
    dataIndex: 'stock',
    key: 'stock',
    width: 100,
    align: 'right',
  },
  {
    title: 'Брак',
    dataIndex: 'defect_stock',
    key: 'defect_stock',
    width: 100,
    align: 'right',
    render: (val: number) => (val > 0 ? <span style={{ color: '#ff4d4f' }}>{val}</span> : val),
  },
]

export default function Dashboard() {
  const [products, setProducts] = useState<ProductWithStock[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(false)
  const [summary, setSummary] = useState<StockSummary | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [pagination, setPagination] = useState({ current: 1, pageSize: 20 })
  const [operationFormOpen, setOperationFormOpen] = useState(false)

  const fetchSummary = async () => {
    try {
      const data = await getStockSummary()
      setSummary(data)
    } catch (error) {
      console.error('Failed to fetch stock summary:', error)
    }
  }

  const fetchProducts = useCallback(
    async (page = 1, pageSize = 20, query = '') => {
      setLoading(true)
      try {
        const skip = (page - 1) * pageSize
        const data = query
          ? await searchProducts(query)
          : await getProducts(skip, pageSize)
        setProducts(data.items)
        setTotal(data.total)
      } catch (error) {
        console.error('Failed to fetch products:', error)
      } finally {
        setLoading(false)
      }
    },
    []
  )

  useEffect(() => {
    fetchSummary()
    fetchProducts()
  }, [fetchProducts])

  const handleSearch = (value: string) => {
    setSearchQuery(value)
    setPagination({ current: 1, pageSize: 20 })
    fetchProducts(1, 20, value)
  }

  const handleTableChange = (pag: { current?: number; pageSize?: number }) => {
    const newPagination = {
      current: pag.current || 1,
      pageSize: pag.pageSize || 20,
    }
    setPagination(newPagination)
    fetchProducts(newPagination.current, newPagination.pageSize, searchQuery)
  }

  const handleOperationSuccess = () => {
    fetchSummary()
    fetchProducts(pagination.current, pagination.pageSize, searchQuery)
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Row gutter={16}>
        <Col span={8}>
          <Card>
            <Statistic
              title="Всего товаров"
              value={summary?.total_products ?? 0}
              prefix={<PackageOutlined />}
              loading={!summary}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Общий остаток"
              value={summary?.total_stock ?? 0}
              prefix={<InboxOutlined />}
              loading={!summary}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="Всего брака"
              value={summary?.total_defect ?? 0}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
              loading={!summary}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Товары">
        <Space style={{ marginBottom: 16 }}>
          <Input.Search
            placeholder="Поиск по штрихкоду"
            allowClear
            enterButton="Поиск"
            size="large"
            onSearch={handleSearch}
            style={{ width: 300 }}
          />
          <Button
            type="primary"
            icon={<PlusOutlined />}
            size="large"
            onClick={() => setOperationFormOpen(true)}
          >
            Провести операцию
          </Button>
        </Space>
        <Spin spinning={loading}>
          <Table
            columns={columns}
            dataSource={products}
            rowKey="id"
            pagination={{
              current: pagination.current,
              pageSize: pagination.pageSize,
              total,
              showSizeChanger: true,
              showTotal: (total) => `Всего ${total} записей`,
            }}
            onChange={handleTableChange}
            scroll={{ x: 1000 }}
          />
        </Spin>
      </Card>

      <OperationForm
        open={operationFormOpen}
        onClose={() => setOperationFormOpen(false)}
        onSuccess={handleOperationSuccess}
      />
    </Space>
  )
}
