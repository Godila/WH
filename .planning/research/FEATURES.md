# Feature Research

**Domain:** WMS / Marketplace Fulfillment System
**Researched:** 2026-02-18
**Confidence:** MEDIUM (based on Wikipedia WMS article, ERPNext documentation, and domain knowledge)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Inventory Tracking** | Core function - must know what's in stock | LOW | Track quantities by SKU, warehouse |
| **Stock Receipt** | Goods arrive, must be recorded | LOW | Record incoming items with quantity |
| **Stock Shipment** | Goods leave, must be recorded | LOW | Record outgoing items |
| **Movement Journal** | Need audit trail of all changes | MEDIUM | History with filtering by date, type, SKU |
| **User Authentication** | Multi-user system requires access control | LOW | JWT auth, basic role separation |
| **Multi-Warehouse** | Even small ops have good/defect split | MEDIUM | Stock vs DefectStock warehouses |
| **Return Handling** | Marketplaces have returns | MEDIUM | Process returned items back to stock or defect |
| **Defect/Write-off** | Damaged goods must be tracked | MEDIUM | Separate defect warehouse, write-off process |
| **Stock Balances** | Know current inventory at any time | LOW | Real-time quantity per warehouse |
| **Basic Reports** | Need to see what's in stock | LOW | Stock levels, recent movements |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Excel Import** | Bulk data entry from suppliers/marketplaces | MEDIUM | Import receipts, stock adjustments |
| **Excel Export** | Reporting to accounting/management | LOW | Export journal, stock balances |
| **Operation Types** | Clear categorization of movements | LOW | 9 distinct types improve clarity |
| **Barcode/QR Scanning** | Speed up data entry, reduce errors | MEDIUM | Requires hardware or mobile app |
| **SKU Search** | Quick lookup of items | LOW | Filter by SKU, name |
| **Stock Alerts** | Low stock, overstock notifications | MEDIUM | Configurable thresholds |
| **Multi-currency** | Import costs in different currencies | MEDIUM | For international suppliers |
| **Batch Operations** | Process multiple items at once | MEDIUM | Bulk receipt, bulk shipment |
| **API Integration** | Connect to marketplace APIs | HIGH | Ozon, WB, Yandex Market sync |
| **Dashboard/Analytics** | KPIs, trends, efficiency metrics | HIGH | Turnover, processing time |
| **Print Labels** | Generate labels for items/boxes | MEDIUM | Thermal printer support |
| **Mobile Interface** | Work from phone/tablet in warehouse | HIGH | PWA or native app |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Complex Picking Optimization** | "Optimize warehouse routes" | Overkill for 2-3 users, 2 warehouses | Simple location-based lookup |
| **Real-time WebSocket Updates** | "See changes instantly" | Unnecessary complexity, infrastructure cost | Polling or manual refresh |
| **Advanced Permission System** | "Granular role control" | Overkill for 2-3 users | 2 roles: admin, operator |
| **Multi-tenant Architecture** | "Support multiple companies" | Massive complexity for single-company use | Single tenant, simple auth |
| **Automated Reordering** | "Auto-purchase when low" | Business logic varies, risky automation | Stock alerts + manual decision |
| **Complex Workflow Engine** | "Configurable approval flows" | Hard to debug, overkill for small team | Simple status transitions |
| **IoT Device Integration** | "Connect scales, conveyors" | Hardware dependency, maintenance burden | Manual entry with validation |
| **Predictive Analytics** | "AI forecasting" | Data requirements, overkill for MVP | Historical reports + human judgment |

## Feature Dependencies

```
[User Auth]
    └──required by──> [All Operations] (track who did what)

[Warehouses]
    └──required by──> [Stock Balances]
    └──required by──> [Movement Journal]

[Inventory Items/SKUs]
    └──required by──> [Stock Receipt]
    └──required by──> [Stock Shipment]
    └──required by──> [Return Handling]
    └──required by──> [Defect/Write-off]

[Stock Receipt/Shipment]
    └──feeds──> [Movement Journal]
    └──feeds──> [Stock Balances]

[Movement Journal]
    └──enables──> [Excel Export]
    └──enables──> [Reports/Dashboard]

[Excel Import]
    └──requires──> [Inventory Items]
    └──requires──> [Stock Receipt]

[API Integration]
    └──requires──> [Stock Receipt]
    └──requires──> [Stock Shipment]
    └──requires──> [Stock Balances]

[Barcode Scanning]
    └──requires──> [Mobile Interface] (or hardware)

[Dashboard/Analytics]
    └──requires──> [Movement Journal]
    └──requires──> [Stock Balances]
```

### Dependency Notes

- **User Auth requires all Operations:** Every movement must have an audit trail of who performed it
- **Warehouses required for Stock Balances:** Cannot track stock without knowing where it is
- **Inventory Items required for all Operations:** Must have SKU master data before recording movements
- **Movement Journal enables Export/Reports:** Journal is the source of truth for analytics
- **API Integration conflicts with simplicity:** Adds significant complexity; defer until core is stable
- **Barcode Scanning requires Mobile:** Scanning on desktop is awkward; needs mobile UI or hardware

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [x] **User Auth (JWT)** — Already in scope; 2-3 users need access control
- [x] **Multi-Warehouse (Stock + DefectStock)** — Already in scope; core requirement
- [x] **Stock Receipt (RECEIPT, RECEIPT_DEFECT)** — Record incoming goods
- [x] **Stock Shipment (SHIPMENT_RC)** — Record outgoing shipments
- [x] **Return Handling (RETURN_PICKUP, RETURN_DEFECT)** — Process returns
- [x] **Defect Operations (WRITE_OFF, RESTORATION, UTILIZATION)** — Handle damaged goods
- [x] **Self-Purchase (SELF_PURCHASE)** — Internal consumption
- [x] **Movement Journal with Filtering** — Audit trail, core visibility
- [x] **Stock Balances per Warehouse** — Know what's in stock
- [x] **Basic SKU Management** — Add/edit items

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] **Excel Import** — High value for bulk data entry; trigger: manual entry becomes tedious
- [ ] **Excel Export** — Low effort, high value for reporting; trigger: users need reports
- [ ] **SKU Search/Filter** — Trigger: inventory grows beyond ~100 items
- [ ] **Stock Alerts (low stock)** — Trigger: stockouts occur
- [ ] **Basic Dashboard** — Trigger: users want KPI visibility

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Barcode/QR Scanning** — Requires mobile interface or hardware; defer until volume justifies
- [ ] **Marketplace API Integration** — High complexity, requires per-marketplace work; defer until core is stable
- [ ] **Mobile PWA** — Significant UI investment; defer until desktop is validated
- [ ] **Advanced Analytics** — Requires data accumulation; defer until 3+ months of data
- [ ] **Print Labels** — Requires printer integration; defer until volume justifies

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| User Auth (JWT) | HIGH | LOW | P1 |
| Multi-Warehouse | HIGH | LOW | P1 |
| Stock Receipt | HIGH | LOW | P1 |
| Stock Shipment | HIGH | LOW | P1 |
| Return Handling | HIGH | MEDIUM | P1 |
| Defect Operations | HIGH | MEDIUM | P1 |
| Movement Journal | HIGH | MEDIUM | P1 |
| Stock Balances | HIGH | LOW | P1 |
| SKU Management | HIGH | LOW | P1 |
| Excel Import | HIGH | MEDIUM | P2 |
| Excel Export | MEDIUM | LOW | P2 |
| SKU Search | MEDIUM | LOW | P2 |
| Stock Alerts | MEDIUM | MEDIUM | P2 |
| Basic Dashboard | MEDIUM | MEDIUM | P2 |
| Barcode Scanning | MEDIUM | HIGH | P3 |
| Marketplace API | HIGH | HIGH | P3 |
| Mobile Interface | MEDIUM | HIGH | P3 |
| Advanced Analytics | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch (MVP)
- P2: Should have, add when possible (v1.x)
- P3: Nice to have, future consideration (v2+)

## Operation Types Analysis

Based on the 9 operation types specified, here's how they map to warehouse flows:

### Inbound Operations
| Type | From | To | Purpose |
|------|------|-----|---------|
| RECEIPT | Supplier | Stock | New goods arriving |
| RECEIPT_DEFECT | Supplier | DefectStock | Goods received already damaged |
| RETURN_PICKUP | Customer | Stock | Customer return, still good |
| RETURN_DEFECT | Customer | DefectStock | Customer return, damaged |

### Outbound Operations
| Type | From | To | Purpose |
|------|------|-----|---------|
| SHIPMENT_RC | Stock | Customer | Fulfill customer order |
| SELF_PURCHASE | Stock | Consumed | Internal use |
| WRITE_OFF | Stock/Defect | Consumed | Discard damaged goods |
| UTILIZATION | DefectStock | Disposed | Destroy defective items |

### Internal Operations
| Type | From | To | Purpose |
|------|------|-----|---------|
| RESTORATION | DefectStock | Stock | Repair and return to saleable |

## Competitor Feature Analysis

| Feature | Enterprise WMS (SAP, Oracle) | Mid-market (Odoo, ERPNext) | Our Approach |
|---------|------------------------------|----------------------------|--------------|
| Complexity | Very high, months to implement | Moderate, weeks to implement | Minimal, days to implement |
| Warehouses | Unlimited, zones, bins | Multiple, basic zones | 2 warehouses (Stock, Defect) |
| Operations | Configurable workflows | Fixed types with customization | 9 fixed operation types |
| Integration | Full ERP suite | Optional modules | Standalone, API-ready |
| Mobile | Native apps | Web-responsive | Desktop-first, mobile-later |
| Cost | $100K+ | $10K-50K | Near-zero (custom build) |

## Sources

- **Wikipedia WMS Article** (2026-02-06 revision) — WMS complexity levels, core functions
  - https://en.wikipedia.org/wiki/Warehouse_management_system
  - Key insight: Basic WMS = inventory management + location control; Advanced = analytics + optimization
  
- **ERPNext Stock Module Documentation** — Practical WMS implementation reference
  - https://docs.frappe.io/erpnext/user/manual/en/stock
  - Key features: Stock Entry types (Receipt, Transfer, Issue), Stock Balance API, Purchase Return

- **Project Context** — Specific requirements from orchestrator
  - 9 operation types defined
  - 2 warehouses (Stock, DefectStock)
  - 2-3 users
  - JWT auth required
  - Excel import required

---
*Feature research for: WMS / Marketplace Fulfillment*
*Researched: 2026-02-18*
