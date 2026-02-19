import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  DashboardOutlined,
  UnorderedListOutlined,
} from '@ant-design/icons'
import Header from './Header'

const { Sider, Content } = Layout

const menuItems = [
  {
    key: '/',
    icon: <DashboardOutlined />,
    label: 'Дашборд',
  },
  {
    key: '/movements',
    icon: <UnorderedListOutlined />,
    label: 'Журнал движений',
  },
]

export default function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        breakpoint="lg"
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div
          style={{
            height: 64,
            margin: 16,
            color: '#fff',
            fontSize: 18,
            fontWeight: 'bold',
            textAlign: 'center',
          }}
        >
          СКЛАД
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout style={{ marginLeft: 200 }}>
        <Layout.Header
          style={{
            padding: 0,
            background: '#fff',
            borderBottom: '1px solid #f0f0f0',
          }}
        >
          <Header />
        </Layout.Header>
        <Content style={{ margin: 24, overflow: 'initial' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
