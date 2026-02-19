import { useAuthStore } from '@/stores/authStore'
import { Button, Space } from 'antd'
import { LogoutOutlined, UserOutlined } from '@ant-design/icons'

export default function Header() {
  const { user, logout } = useAuthStore()

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'flex-end',
        alignItems: 'center',
        padding: '0 24px',
        height: '100%',
      }}
    >
      <Space>
        <UserOutlined />
        <span>{user?.email}</span>
        <Button type="text" icon={<LogoutOutlined />} onClick={logout}>
          Выйти
        </Button>
      </Space>
    </div>
  )
}
