import { useState, useEffect } from 'react'
import { Select } from 'antd'
import { getDCs, type DistributionCenter } from '@/api/dcs'

interface DCSelectProps {
  value?: number
  onChange?: (value: number | undefined) => void
  style?: React.CSSProperties
  disabled?: boolean
}

export default function DCSelect({ value, onChange, style, disabled }: DCSelectProps) {
  const [dcs, setDCs] = useState<DistributionCenter[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchDCs = async () => {
      setLoading(true)
      try {
        const data = await getDCs()
        setDCs(data)
      } catch (error) {
        console.error('Failed to fetch DCs:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchDCs()
  }, [])

  return (
    <Select
      value={value}
      style={style}
      allowClear
      placeholder="Выберите РЦ"
      loading={loading}
      disabled={disabled}
      onChange={onChange}
      options={dcs.map((dc) => ({ value: dc.id, label: dc.name }))}
    />
  )
}
