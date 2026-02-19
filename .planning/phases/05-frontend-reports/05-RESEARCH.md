# Research: Phase 5 - Frontend & Reports

**Goal:** Менеджеры используют web-интерфейс для ежедневной работы с системой
**Researched:** 2026-02-19
**Status:** Ready for Planning

---

## 1. Stack Confirmation

### Confirmed Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 18.3.1 | UI framework |
| **TypeScript** | 5.9.x | Type safety |
| **Vite** | 7.x | Build tool, dev server |
| **Ant Design** | 5.x | UI components (use 5.x not 6.x for stability) |
| **Zustand** | 5.x | State management |
| **Axios** | 1.x | HTTP client with interceptors |
| **React Router** | 7.x | Client-side routing |

### Why These Choices

- **Vite over CRA**: 10-100x faster builds, native ESM, instant HMR
- **Zustand over Redux**: 90% less boilerplate, no providers needed, TypeScript-first
- **Ant Design 5.x**: Enterprise-grade components, Russian locale, perfect for WMS
- **Axios**: Interceptors for JWT refresh and 401 handling

---

## 2. Recommended Project Structure

```
frontend/
├── src/
│   ├── api/                      # API layer
│   │   ├── client.ts             # Axios instance with interceptors
│   │   ├── auth.ts               # Login, logout, me
│   │   ├── products.ts           # Products CRUD
│   │   ├── stock.ts              # Movements, summary
│   │   └── types.ts              # API response types
│   │
│   ├── components/               # Reusable components
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx     # Main layout with sidebar
│   │   │   └── Header.tsx        # Top bar with user info
│   │   ├── common/
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   └── products/
│   │       └── ProductSelect.tsx # Autocomplete for products
│   │
│   ├── pages/                    # Route pages
│   │   ├── Login.tsx             # UI-01
│   │   ├── Dashboard.tsx         # UI-02, UI-03, UI-04, RPT-02
│   │   ├── Movements/
│   │   │   ├── Journal.tsx       # UI-08, UI-09, UI-10
│   │   │   └── OperationForm.tsx # UI-05, UI-06, UI-07
│   │   └── NotFound.tsx
│   │
│   ├── stores/                   # Zustand stores
│   │   ├── authStore.ts          # Token, user, login/logout
│   │   └── uiStore.ts            # Sidebar state, modals
│   │
│   ├── hooks/                    # Custom hooks
│   │   ├── useAuth.ts            # Auth convenience hook
│   │   └── useApi.ts             # API state with loading/error
│   │
│   ├── types/                    # TypeScript types
│   │   ├── product.ts
│   │   ├── movement.ts
│   │   └── user.ts
│   │
│   ├── utils/                    # Utilities
│   │   ├── colors.ts             # UI-10 color coding
│   │   └── formatters.ts         # Date, number formatting
│   │
│   ├── App.tsx                   # Root component with routes
│   ├── main.tsx                  # Entry point
│   └── vite-env.d.ts
│
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── .env                          # VITE_API_URL=http://localhost:8000
```

---

## 3. Component Mapping (Requirements → Components)

| Requirement | Component | Ant Design Components |
|-------------|-----------|----------------------|
| UI-01: Login page | `Login.tsx` | `Form`, `Input`, `Button` |
| UI-02: Products table | `Dashboard.tsx` | `Table`, `Statistic` |
| UI-03: Search barcode/SKU | `Dashboard.tsx` | `Input.Search` or `AutoComplete` |
| UI-04: Statistics | `Dashboard.tsx` | `Statistic`, `Card`, `Row`, `Col` |
| UI-05: Operation form | `OperationForm.tsx` | `Form`, `Select`, `InputNumber`, `Modal` |
| UI-06: Dynamic fields | `OperationForm.tsx` | `Form.Item` conditional rendering |
| UI-07: Product autocomplete | `ProductSelect.tsx` | `AutoComplete` or `Select` with `showSearch` |
| UI-08: Movement journal | `Journal.tsx` | `Table` with filters |
| UI-09: Pagination | `Journal.tsx` | `Table` pagination prop |
| UI-10: Color coding | `Journal.tsx` | `Tag` with color props |
| UI-11: Error handling | `api/client.ts` | `message.error()` |
| UI-12: Loading states | Components | `Spin`, `Skeleton`, button `loading` prop |
| UI-13: Token redirect | `api/client.ts` + router | 401 interceptor + redirect |
| RPT-02: Dashboard stats | `Dashboard.tsx` | `Statistic` components |

---

## 4. API Client Setup

### Axios Instance with Interceptors

```typescript
// src/api/client.ts
import axios from 'axios'
import { message } from 'antd'
import { useAuthStore } from '@/stores/authStore'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

// Request: Add JWT token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response: Handle 401 and errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
      return Promise.reject(error)
    }
    
    const detail = error.response?.data?.detail || 'Ошибка сервера'
    message.error(detail)
    return Promise.reject(error)
  }
)

export default api
```

### API Functions

```typescript
// src/api/auth.ts
import api from './client'
import type { User } from '@/types/user'

export async function login(email: string, password: string) {
  const { data } = await api.post<{ access_token: string }>('/api/auth/login', 
    new URLSearchParams({ username: email, password }))
  return data.access_token
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>('/api/auth/me')
  return data
}
```

---

## 5. Auth Flow Implementation

### Zustand Auth Store

```typescript
// src/stores/authStore.ts
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { login as apiLogin, getMe } from '@/api/auth'
import type { User } from '@/types/user'

interface AuthState {
  token: string | null
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isLoading: false,
      
      login: async (email, password) => {
        set({ isLoading: true })
        const token = await apiLogin(email, password)
        set({ token })
        await get().fetchUser()
        set({ isLoading: false })
      },
      
      logout: () => {
        set({ token: null, user: null })
      },
      
      fetchUser: async () => {
        const { token } = get()
        if (!token) return
        try {
          const user = await getMe()
          set({ user })
        } catch {
          set({ token: null, user: null })
        }
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ token: state.token }),
    }
  )
)
```

### Protected Route Component

```typescript
// src/components/common/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token)
  const location = useLocation()
  
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  
  return <>{children}</>
}
```

### App Routes

```typescript
// src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ConfigProvider, ruRU } from 'antd'
import { ProtectedRoute } from '@/components/common/ProtectedRoute'
import Login from '@/pages/Login'
import Dashboard from '@/pages/Dashboard'
import Journal from '@/pages/Movements/Journal'
import AppLayout from '@/components/layout/AppLayout'

export default function App() {
  return (
    <ConfigProvider locale={ruRU}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/movements" element={<Journal />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ConfigProvider>
  )
}
```

---

## 6. Dynamic Form Fields (UI-06)

### Operation Type → Required Fields Mapping

```typescript
// src/utils/operationFields.ts
export const OPERATION_CONFIG = {
  receipt: { sourceRequired: false, dcRequired: false },
  receipt_defect: { sourceRequired: false, dcRequired: false },
  shipment_rc: { sourceRequired: false, dcRequired: true },    // DC required
  return_pickup: { sourceRequired: true, dcRequired: false },  // Source required
  return_defect: { sourceRequired: true, dcRequired: false },  // Source required
  self_purchase: { sourceRequired: true, dcRequired: false },  // Source required
  write_off: { sourceRequired: false, dcRequired: false },
  restoration: { sourceRequired: false, dcRequired: false },
  utilization: { sourceRequired: false, dcRequired: false },
}

export const OPERATION_LABELS = {
  receipt: 'Приёмка годного',
  receipt_defect: 'Приёмка брака',
  shipment_rc: 'Отгрузка в РЦ',
  return_pickup: 'Возврат годного с ПВЗ',
  return_defect: 'Возврат брака',
  self_purchase: 'Самовыкуп',
  write_off: 'Списание в брак',
  restoration: 'Восстановление',
  utilization: 'Утилизация',
}
```

### Form with Conditional Fields

```tsx
// src/pages/Movements/OperationForm.tsx
import { Form, Select, InputNumber, Modal } from 'antd'
import { OPERATION_CONFIG, OPERATION_LABELS } from '@/utils/operationFields'

export function OperationForm({ open, onClose }: Props) {
  const [form] = Form.useForm()
  const operationType = Form.useWatch('operation_type', form)
  const config = OPERATION_CONFIG[operationType] || {}

  return (
    <Modal open={open} onCancel={onClose} onOk={() => form.submit()}>
      <Form form={form} onFinish={handleSubmit}>
        <Form.Item name="operation_type" label="Тип операции" rules={[{ required: true }]}>
          <Select options={Object.entries(OPERATION_LABELS).map(
            ([value, label]) => ({ value, label })
          )} />
        </Form.Item>
        
        <Form.Item name="product_id" label="Товар" rules={[{ required: true }]}>
          <ProductSelect />
        </Form.Item>
        
        <Form.Item name="quantity" label="Количество" rules={[{ required: true }]}>
          <InputNumber min={1} style={{ width: '100%' }} />
        </Form.Item>
        
        {/* Conditional: Source */}
        {config.sourceRequired && (
          <Form.Item name="source_id" label="Источник" rules={[{ required: true }]}>
            <SourceSelect />
          </Form.Item>
        )}
        
        {/* Conditional: Distribution Center */}
        {config.dcRequired && (
          <Form.Item name="distribution_center_id" label="РЦ" rules={[{ required: true }]}>
            <DCSelect />
          </Form.Item>
        )}
      </Form>
    </Modal>
  )
}
```

---

## 7. Color Coding (UI-10)

### Movement Type Colors

```typescript
// src/utils/colors.ts
export const MOVEMENT_COLORS: Record<string, string> = {
  // Green: Good stock operations (Stock +=)
  receipt: 'green',
  return_pickup: 'green',
  self_purchase: 'green',
  restoration: 'green',
  
  // Orange: Defect operations
  receipt_defect: 'orange',
  return_defect: 'orange',
  write_off: 'orange',
  
  // Blue: Shipments
  shipment_rc: 'blue',
  
  // Red: Utilization
  utilization: 'red',
}

export function getMovementColor(type: string): string {
  return MOVEMENT_COLORS[type] || 'default'
}
```

### Table Column with Color

```tsx
// In Journal.tsx
const columns = [
  {
    title: 'Тип операции',
    dataIndex: 'operation_type',
    render: (type: string) => (
      <Tag color={getMovementColor(type)}>
        {OPERATION_LABELS[type]}
      </Tag>
    ),
  },
  // ... other columns
]
```

---

## 8. Product Autocomplete (UI-07)

```tsx
// src/components/products/ProductSelect.tsx
import { Select } from 'antd'
import { useState, useEffect } from 'react'
import { searchProducts } from '@/api/products'
import { debounce } from 'lodash'

export function ProductSelect({ value, onChange }: Props) {
  const [options, setOptions] = useState([])
  const [loading, setLoading] = useState(false)
  
  const handleSearch = debounce(async (query: string) => {
    if (!query || query.length < 2) {
      setOptions([])
      return
    }
    setLoading(true)
    try {
      const { items } = await searchProducts(query)
      setOptions(items.map((p) => ({
        value: p.id,
        label: `${p.barcode} | ${p.seller_sku || ''} | ${p.brand || ''}`,
      })))
    } finally {
      setLoading(false)
    }
  }, 300)
  
  return (
    <Select
      showSearch
      filterOption={false}
      onSearch={handleSearch}
      options={options}
      loading={loading}
      placeholder="Поиск по баркоду/артикулу"
      value={value}
      onChange={onChange}
    />
  )
}
```

---

## 9. Loading States (UI-12)

### Patterns

```tsx
// Page-level loading
const { data, isLoading } = useQuery('/api/products')

if (isLoading) {
  return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />
}

// Button loading
<Button type="primary" loading={isSubmitting} onClick={handleSubmit}>
  Сохранить
</Button>

// Table loading
<Table loading={isLoading} dataSource={data} columns={columns} />

// Skeleton for cards
<Skeleton active loading={isLoading}>
  <Statistic title="Всего товаров" value={stats.total_products} />
</Skeleton>
```

---

## 10. Key Pitfalls to Avoid

### 1. JWT Token Expiration
**Problem:** Token expires mid-session, API calls fail
**Solution:** Axios 401 interceptor → clear store → redirect to login

### 2. Zustand Persist + SSR
**Problem:** Hydration mismatch with localStorage
**Solution:** Use `skipHydration: true` or check `typeof window !== 'undefined'`

### 3. Dynamic Form Validation
**Problem:** Backend validates conditional fields, frontend doesn't
**Solution:** Use `Form.useWatch` + conditional `rules={[{ required: config.sourceRequired }]}`

### 4. Debounced Search Memory Leak
**Problem:** Component unmounts before debounced call completes
**Solution:** Use `useEffect` cleanup or `useDeferredValue` in React 18

### 5. Table Pagination State
**Problem:** Filters reset when page changes
**Solution:** Keep filters in URL params or separate Zustand store

### 6. CORS Issues
**Problem:** Frontend can't reach backend API
**Solution:** Configure Vite proxy or backend CORS middleware

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

### 7. Russian Locale
**Problem:** Ant Design shows English dates/tables by default
**Solution:** Wrap with `<ConfigProvider locale={ruRU}>`

---

## 11. Implementation Order (Recommended)

### Wave 1: Foundation
1. Vite + React + TypeScript setup
2. Ant Design + Russian locale
3. Axios client with interceptors
4. Zustand auth store
5. Login page + protected routes

### Wave 2: Dashboard
1. AppLayout with navigation
2. Products table with pagination
3. Search by barcode/SKU
4. Statistics cards (total products, stock, defect)

### Wave 3: Operations
1. Operation form modal
2. Product autocomplete
3. Dynamic fields based on operation type
4. Sources/DCs dropdowns

### Wave 4: Movement Journal
1. Movements table with pagination
2. Filters (type, date, product)
3. Color coding for operation types
4. Loading/error states

### Wave 5: Polish
1. Error handling with message.error()
2. Loading states everywhere
3. Responsive layout
4. Final testing

---

## 12. Files to Create (Checklist)

### Must Have
- [ ] `frontend/package.json`
- [ ] `frontend/vite.config.ts`
- [ ] `frontend/tsconfig.json`
- [ ] `frontend/index.html`
- [ ] `frontend/src/main.tsx`
- [ ] `frontend/src/App.tsx`
- [ ] `frontend/src/api/client.ts`
- [ ] `frontend/src/stores/authStore.ts`
- [ ] `frontend/src/pages/Login.tsx`
- [ ] `frontend/src/pages/Dashboard.tsx`
- [ ] `frontend/src/pages/Movements/Journal.tsx`
- [ ] `frontend/src/pages/Movements/OperationForm.tsx`

### Nice to Have
- [ ] `frontend/src/components/layout/AppLayout.tsx`
- [ ] `frontend/src/components/products/ProductSelect.tsx`
- [ ] `frontend/src/utils/colors.ts`
- [ ] `frontend/src/utils/operationFields.ts`

---

## 13. Commands to Start

```bash
# Create frontend
npm create vite@latest frontend -- --template react-ts
cd frontend

# Install dependencies
npm install antd @ant-design/icons zustand axios react-router-dom
npm install -D @types/react @types/react-dom
```

---

*Research complete. Ready for phase planning.*
