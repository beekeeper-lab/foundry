# Data Model Specification: [Model Name]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Data Engineer name]           |
| Related links | [Task / design spec links]     |
| Status        | Draft / Reviewed / Approved    |

*Schema definition for a data model. Covers structure, relationships, constraints, and migration plan.*

---

## Model Overview

- **Purpose:** [What business domain does this model represent?]
- **Model type:** [Dimensional / Normalized / Hybrid / Flat]
- **Target system:** [Warehouse / Lake / Application DB]
- **Grain:** [What does one row represent?]

---

## Entity Definitions

### [Table Name]

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| [e.g., id] | [e.g., BIGINT] | [No] | [AUTO_INCREMENT] | [Primary key] |
| [e.g., customer_id] | [e.g., BIGINT] | [No] | — | [FK to dim_customer] |
| [e.g., order_date] | [e.g., DATE] | [No] | — | [Date order was placed] |
| [e.g., total_amount] | [e.g., DECIMAL(12,2)] | [No] | [0.00] | [Order total including tax] |
| [e.g., created_at] | [e.g., TIMESTAMP] | [No] | [CURRENT_TIMESTAMP] | [Row creation timestamp] |
| [e.g., updated_at] | [e.g., TIMESTAMP] | [No] | [CURRENT_TIMESTAMP] | [Row last modified timestamp] |

**Constraints:**
- Primary key: `id`
- Foreign keys: `customer_id → dim_customer(id)`
- Indexes: `idx_order_date (order_date)`, `idx_customer_id (customer_id)`
- Partition: `PARTITION BY RANGE (order_date)` -- monthly partitions

---

## Relationships

| From Table | From Column | To Table | To Column | Cardinality |
|-----------|-------------|----------|-----------|-------------|
| [e.g., fact_orders] | [customer_id] | [dim_customer] | [id] | [Many-to-one] |

---

## Migration Plan

### Forward Migration

```sql
-- Migration: [NNN]_create_[table_name]
-- Description: [What this migration does]

-- [DDL statements here]
```

### Rollback Migration

```sql
-- Rollback: [NNN]_create_[table_name]
-- Description: [Reverses the forward migration]

-- [DDL statements here]
```

---

## Query Patterns

*Expected query access patterns that inform indexing and partitioning decisions.*

| Query Pattern | Frequency | Key Columns | Notes |
|--------------|-----------|-------------|-------|
| [e.g., Daily order summary by customer] | [High] | [order_date, customer_id] | [Drives partition and index choice] |

---

## Data Quality Expectations

| Column | Rule | Threshold |
|--------|------|-----------|
| [e.g., id] | [Unique, not null] | [100%] |
| [e.g., total_amount] | [>= 0] | [100%] |
| [e.g., customer_id] | [Referential integrity] | [100%] |
