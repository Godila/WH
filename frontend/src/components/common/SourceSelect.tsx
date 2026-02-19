import { useState, useEffect } from 'react'
import { Select } from 'antd'
import { getSources, type Source } from '@/api/sources'

interface SourceSelectProps {
  value?: number
  onChange?: (value: number | undefined) => void
  style?: React.CSSProperties
  disabled?: boolean
}

export default function SourceSelect({ value, onChange, style, disabled }: SourceSelectProps) {
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchSources = async () => {
      setLoading(true)
      try {
        const data = await getSources()
        setSources(data)
      } catch (error) {
        console.error('Failed to fetch sources:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchSources()
  }, [])

  return (
    <Select
      value={value}
      style={style}
      allowClear
      placeholder="Выберите ПВЗ"
      loading={loading}
      disabled={disabled}
      onChange={onChange}
      options={sources.map((s) => ({ value: s.id, label: s.name }))}
    />
  )
}
