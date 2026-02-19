import { Component, type ReactNode, type ErrorInfo } from 'react'
import { Result, Button } from 'antd'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error)
    console.error('Error info:', errorInfo.componentStack)
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          minHeight: '100vh',
          background: '#f0f2f5'
        }}>
          <Result
            status="error"
            title="Произошла ошибка"
            subTitle={this.state.error?.message || 'Что-то пошло не так'}
            extra={
              <Button type="primary" onClick={this.handleReload}>
                Перезагрузить
              </Button>
            }
          />
        </div>
      )
    }

    return this.props.children
  }
}
