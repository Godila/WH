import { useState, useCallback, useRef, useEffect } from 'react'
import { Select, Spin } from 'antd'
import { searchProducts } from '@/api/products'
import type { Product } from '@/types/product'

interface ProductSelectProps {
  value?: number
  onChange?: (value: number | undefined) => void
  style?: React.CSSProperties
  disabled?: boolean
}

export default function ProductSelect({ value, onChange, style, disabled }: ProductSelectProps) {
  const [options, setOptions] = useState<{ value: number; label: string }[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const debounceRef = useRef<NodeJS.Timeout | null>(null)

  const handleSearch = useCallback((query: string) => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current)
    }

    if (query.length < 2) {
      setOptions([])
      return
    }

    debounceRef.current = setTimeout(async () => {
      setLoading(true)
      try {
        const data = await searchProducts(query)
        const formatted = data.items.map((p) => ({
          value: p.id,
          label: `${p.barcode} | ${p.seller_sku || '-'} | ${p.brand || '-'}`,
          product: p,
        }))
        setOptions(formatted)
      } catch (error) {
        console.error('Failed to search products:', error)
      } finally {
        setLoading(false)
      }
    }, 300)
  }, [])

  const handleSelect = (selectedValue: number, option: { product: Product }) => {
    setSelectedProduct(option.product)
    onChange?.(selectedValue)
  }

  const handleClear = () => {
    setSelectedProduct(null)
    setOptions([])
    onChange?.(undefined)
  }

  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current)
      }
    }
  }, [])

  return (
    <Select
      value={value}
      style={style}
      showSearch
      allowClear
      filterOption={false}
      onSearch={handleSearch}
      onSelect={handleSelect}
      onClear={handleClear}
      placeholder="Минимум 2 символа для поиска"
      notFoundContent={loading ? <Spin size="small" /> : 'Ничего не найдено'}
      loading={loading}
      disabled={disabled}
      options={options}
    />
  )
}
