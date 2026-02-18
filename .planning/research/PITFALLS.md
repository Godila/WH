# Pitfalls Research: WMS/Fulfillment System

**Domain:** Warehouse Management System / Fulfillment for Russian Marketplaces
**Researched:** 2026-02-18
**Confidence:** MEDIUM (based on authoritative database docs, Prisma docs, distributed systems patterns; web search had issues)

---

## Critical Pitfalls

### Pitfall 1: TOCTOU Race Condition on Inventory

**What goes wrong:**
Two operations check available stock simultaneously, both see sufficient quantity, both proceed to decrement — resulting in negative inventory. Classic "Time-of-check to time-of-use" bug.

**Example:**
```
Operation A: READ stock = 10, needs 5 ✓
Operation B: READ stock = 10, needs 8 ✓
Operation A: WRITE stock = 5
Operation B: WRITE stock = 2 (expected) → actual stock = -3 ✗
```

**Why it happens:**
- Using Read Committed isolation level (PostgreSQL default)
- Check and update in separate operations
- No explicit locking or atomic operations

**How to avoid:**
1. Use Prisma interactive transactions with conditional updates:
   ```typescript
   await prisma.$transaction(async (tx) => {
     // Single atomic operation: validate AND update
     const result = await tx.inventory.updateMany({
       where: { 
         productId, 
         quantity: { gte: amount } // Check happens atomically with update
       },
       data: { quantity: { decrement: amount } }
     });
     if (result.count === 0) throw new Error("Insufficient stock");
   });
   ```
2. For complex validations, use `SELECT FOR UPDATE` or Repeatable Read isolation
3. Implement database-level constraints (CHECK for non-negative stock)

**Warning signs:**
- Intermittent negative inventory reports
- "Ghost stock" (system shows available but doesn't exist)
- Orders failing after initial acceptance

**Phase to address:** Phase 1 (Core Inventory Operations)

---

### Pitfall 2: Partial Operation Failure (Non-Atomic Multi-Step Operations)

**What goes wrong:**
Operation requires multiple database writes (e.g., create inventory movement + update stock + create audit log). If any step fails mid-way, data becomes inconsistent.

**Why it happens:**
- Each operation runs independently without transaction wrapping
- Network timeout between operations
- Unexpected errors not caught properly

**How to avoid:**
1. Wrap ALL related operations in a single Prisma transaction:
   ```typescript
   await prisma.$transaction([
     prisma.inventoryMovement.create({ data: movement }),
     prisma.inventory.update({ where: { id }, data: { quantity: { decrement: qty } } }),
     prisma.auditLog.create({ data: log })
   ]);
   ```
2. For operations with business logic between steps, use interactive transactions
3. Never commit partial state — either all succeed or all roll back

**Warning signs:**
- Audit logs missing corresponding inventory changes
- Movements without stock updates (or vice versa)
- Inconsistencies between related tables

**Phase to address:** Phase 1 (Core Inventory Operations)

---

### Pitfall 3: Excel Import Memory Exhaustion

**What goes wrong:**
Importing large Excel files (10K+ rows) loads entire file into memory, causing OOM crashes or extreme slowdowns.

**Why it happens:**
- Using `workbook.xlsx.readFile()` which loads entire file into memory
- Processing all rows before any database writes
- No streaming or chunking strategy

**How to avoid:**
1. Use ExcelJS streaming API for reading:
   ```typescript
   const workbook = new ExcelJS.Workbook();
   await workbook.xlsx.readFile(filename);
   // Process in chunks of 500-1000 rows
   ```
2. Batch database operations (not one transaction per row):
   ```typescript
   const BATCH_SIZE = 500;
   for (let i = 0; i < rows.length; i += BATCH_SIZE) {
     const batch = rows.slice(i, i + BATCH_SIZE);
     await prisma.$transaction(batch.map(row => upsertOperation(row)));
   }
   ```
3. Implement row-by-row validation BEFORE any database writes
4. Set memory limits and timeouts for import endpoints

**Warning signs:**
- Node.js OOM errors during imports
- Import taking 10x longer for 2x more rows
- Server becoming unresponsive during large imports

**Phase to address:** Phase 2 (Excel Import)

---

### Pitfall 4: Silent Excel Data Corruption

**What goes wrong:**
Excel imports silently corrupt data due to type coercion, encoding issues, or malformed cells. Numbers become strings, dates shift by timezone, leading zeros disappear.

**Why it happens:**
- Excel has no strict schema
- User edits break expected formats
- No server-side validation before processing

**How to avoid:**
1. Define strict validation schema per column:
   ```typescript
   const rowSchema = z.object({
     sku: z.string().min(1).max(50),
     quantity: z.number().int().nonnegative(),
     price: z.number().positive().optional(),
   });
   ```
2. Validate ALL rows before ANY database write
3. Report errors with row numbers and specific field failures
4. Preserve original string values for SKUs (don't convert to numbers)

**Common corruptions:**
| Field Type | Common Corruption | Prevention |
|------------|-------------------|------------|
| SKU/Article | Leading zeros stripped, E notation | Store as string, validate regex |
| Quantity | Float instead of int, empty as 0 | Explicit int parsing, reject empty |
| Date | Timezone shifts, different formats | Parse with explicit timezone |
| Price | Comma vs period decimals | Normalize before parsing |

**Warning signs:**
- Products with "SKU not found" that exist in system
- Negative prices or absurd quantities
- Dates shifted by ±1 day

**Phase to address:** Phase 2 (Excel Import)

---

### Pitfall 5: Missing Idempotency for Operations

**What goes wrong:**
User double-clicks "Submit" or network timeout triggers retry — same operation executes twice, duplicating inventory changes.

**Why it happens:**
- No idempotency key in API design
- Operations not naturally idempotent
- Client-side retry logic without deduplication

**How to avoid:**
1. Require idempotency key for mutating operations:
   ```typescript
   // Client sends: { idempotencyKey: "uuid-v4", operation: "receive", ... }
   // Check if key already processed
   const existing = await prisma.idempotencyKey.findUnique({ 
     where: { key: idempotencyKey } 
   });
   if (existing) return existing.result; // Return cached result
   ```
2. Cache operation results with idempotency key
3. Use unique constraints on idempotency key + user + time window

**Warning signs:**
- Duplicate inventory movements with same timestamp
- Stock discrepancies after network issues
- Users reporting "double bookings"

**Phase to address:** Phase 1 (Core Inventory Operations)

---

### Pitfall 6: Ambiguous Operation Type Effects

**What goes wrong:**
With 9 operation types, developers confuse which operations increase vs decrease stock, leading to incorrect inventory adjustments.

**Why it happens:**
- No clear documentation of operation semantics
- Similar names with different effects (e.g., "return" vs "return to supplier")
- Business logic spread across codebase

**How to avoid:**
1. Define operation types with explicit effects:
   ```typescript
   const OPERATION_EFFECTS = {
     RECEIVE: { quantity: +1, reserved: 0 },
     SHIP: { quantity: -1, reserved: -1 },
     RESERVE: { quantity: 0, reserved: +1 },
     RETURN_CUSTOMER: { quantity: +1, reserved: 0 },
     RETURN_SUPPLIER: { quantity: -1, reserved: 0 },
     ADJUSTMENT_PLUS: { quantity: +1, reserved: 0 },
     ADJUSTMENT_MINUS: { quantity: -1, reserved: 0 },
     TRANSFER_IN: { quantity: +1, reserved: 0 },
     TRANSFER_OUT: { quantity: -1, reserved: 0 },
   } as const;
   ```
2. Single source of truth for operation logic
3. Type-safe enums, not magic strings
4. Unit tests for each operation type's effect

**Warning signs:**
- Stock increasing when it should decrease
- Reserved quantity not matching orders
- "Mystery" stock changes without clear cause

**Phase to address:** Phase 1 (Core Inventory Operations)

---

### Pitfall 7: Lost Update Problem in Excel Upserts

**What goes wrong:**
Excel import updates product A while another operation is modifying it. Import overwrites concurrent changes with stale data.

**Why it happens:**
- Read-modify-write pattern without version check
- No optimistic locking on product updates
- Long-running import gives time for concurrent modifications

**How to avoid:**
1. Use optimistic locking with version field:
   ```typescript
   await prisma.product.update({
     where: { id, version: currentVersion },
     data: { ...updates, version: { increment: 1 } }
   });
   // If version mismatch, update fails
   ```
2. For bulk imports, only update fields present in Excel (partial updates)
3. Log conflicts for manual review
4. Consider "last write wins" vs "fail on conflict" strategy upfront

**Warning signs:**
- Product attributes reverting to old values
- Users reporting changes "disappearing"
- Inconsistencies between import logs and actual data

**Phase to address:** Phase 2 (Excel Import)

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| No transaction on simple operations | Faster development | Race conditions under load | Never for inventory |
| In-memory validation only | Simpler code | Invalid data in DB | Only for non-critical fields |
| Sequential row-by-row import | Easier error handling | Hours-long imports | <100 rows only |
| Skip audit logging | Less DB writes | No recovery path, compliance issues | Never |
| Hardcoded operation effects | Faster to write | Impossible to configure | Never — use lookup table |
| JWT in localStorage | Simpler auth flow | XSS vulnerability | Never — use httpOnly cookies |

---

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Marketplace API | Assume always available | Implement retry with exponential backoff, circuit breaker |
| Marketplace API | Sync inventory without confirmation | Require acknowledgment before committing local change |
| Excel files | Trust client-side validation | Always validate server-side |
| Reporting | Query production DB directly | Use read replica or materialized views |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| N+1 queries on inventory listing | Slow page loads, high DB load | Use Prisma include/select for eager loading | 100+ products |
| Full table scan for SKU lookup | Search takes seconds | Index on SKU, article fields | 10K+ products |
| One transaction per Excel row | Import takes hours | Batch operations (500-1000 rows per transaction) | 1K+ rows |
| No pagination on inventory view | Browser OOM, slow renders | Server-side pagination, cursor-based | 1000+ rows in view |
| Synchronous stock reservation | API timeouts during peak | Async reservation with confirmation | High concurrent orders |

---

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| JWT secret in environment without rotation | Token forgery if leaked | Rotate secrets, use short expiry, refresh tokens |
| No rate limiting on import endpoint | DoS via large file uploads | Limit file size, rate limit per user |
| SQL in Excel field names | SQL injection | Whitelist allowed columns, parameterized queries |
| Exposing internal SKUs in public API | Information disclosure | Use external IDs, map internally |
| No audit trail for stock changes | Fraud goes undetected | Log ALL inventory changes with user, timestamp, reason |

---

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No feedback during long import | User thinks it's broken | Progress bar, chunk completion updates |
| Generic error messages | User can't fix the problem | Specific: "Row 42: SKU 'ABC' not found in system" |
| No undo for operations | One mistake ruins inventory | Reversibility for reversible operations |
| Showing technical IDs | Confusion, data entry errors | Use human-readable SKUs, names |
| No confirmation for large operations | Accidental mass changes | Require confirmation for bulk operations |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Transaction rollback:** Often missing proper rollback handling — verify all code paths roll back on error
- [ ] **Negative stock prevention:** Often missing at DB level — verify CHECK constraint exists
- [ ] **Excel validation:** Often validates only success cases — verify error row reporting works
- [ ] **Audit logging:** Often added later — verify ALL operations create audit entries from day one
- [ ] **Idempotency:** Often forgotten — verify retry scenarios don't duplicate operations
- [ ] **Concurrent access:** Often untested — verify behavior when two users edit same product
- [ ] **Operation type validation:** Often accepts any string — verify only defined types are allowed

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Negative inventory | MEDIUM | Identify affected SKUs, reverse problematic movements, reconcile with physical count |
| Duplicate operations | LOW | Find by idempotency key/timestamp, reverse duplicate entries |
| Corrupted import | MEDIUM | Rollback to pre-import backup, fix validation, re-import |
| Lost updates | HIGH | Restore from audit log if available, otherwise manual reconciliation |
| Missing audit trail | HIGH | Often unrecoverable — implement forensic DB analysis |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| TOCTOU Race Condition | Phase 1: Core Inventory | Load test with concurrent operations |
| Partial Operation Failure | Phase 1: Core Inventory | Kill process mid-transaction, verify rollback |
| Excel Memory Exhaustion | Phase 2: Excel Import | Test with 50K+ row files |
| Silent Excel Corruption | Phase 2: Excel Import | Test with malformed files, verify errors |
| Missing Idempotency | Phase 1: Core Inventory | Send duplicate requests, verify single execution |
| Ambiguous Operation Effects | Phase 1: Core Inventory | Unit test each operation type |
| Lost Update Problem | Phase 2: Excel Import | Concurrent edit + import, verify conflict handling |

---

## Sources

- PostgreSQL Transaction Isolation Documentation (https://www.postgresql.org/docs/current/transaction-iso.html) — HIGH confidence
- Prisma Transaction Documentation (Context7) — HIGH confidence
- Baeldung: Race Conditions (https://www.baeldung.com/cs/race-conditions) — HIGH confidence
- ExcelJS Documentation (Context7) — HIGH confidence
- Martin Fowler: Patterns of Distributed Systems — HIGH confidence
- Domain knowledge: WMS/fulfillment patterns — MEDIUM confidence (industry experience)

---
*Pitfalls research for: WMS/Fulfillment System*
*Researched: 2026-02-18*
