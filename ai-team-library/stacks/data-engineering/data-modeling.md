# Data Modeling

Standards for analytical data modeling in data warehouses. Dimensional modeling
(Kimball) is the default for analytics workloads. Data Vault is the alternative
for environments requiring full auditability and multi-source integration.

---

## Defaults

| Concern | Default | Alternatives |
|---------|---------|--------------|
| **Methodology** | Kimball dimensional modeling (star schema) | Data Vault 2.0 for audit-heavy, multi-source integration environments |
| **Fact tables** | One fact per business process (e.g., `fct_orders`, `fct_page_views`) | Transaction grain by default; periodic snapshot for cumulative metrics |
| **Dimension tables** | Conformed dimensions shared across facts (`dim_customer`, `dim_date`) | Junk dimensions for low-cardinality flag combinations |
| **Slowly changing dimensions** | SCD Type 2 (track history with `valid_from`/`valid_to`) | SCD Type 1 (overwrite) for attributes where history is not needed |
| **Surrogate keys** | Integer surrogate keys on all dimensions | Hash keys (MD5/SHA-256) in Data Vault hubs and links |
| **Naming** | `fct_` prefix for facts, `dim_` prefix for dimensions, `stg_` for staging | `hub_`, `sat_`, `lnk_` prefixes for Data Vault entities |
| **Grain** | Explicitly documented in every fact table definition | — |

---

## Do / Don't

- **Do** document the grain of every fact table. The grain is the most important decision in dimensional modeling — it defines what one row represents.
- **Do** build conformed dimensions that are shared across multiple fact tables. This enables cross-process analysis.
- **Do** use SCD Type 2 for any dimension attribute where business users need historical reporting (e.g., customer segment changes over time).
- **Do** create a `dim_date` table with pre-computed fiscal periods, holidays, and week indicators. Never compute date logic in queries.
- **Do** separate staging models (raw source mirrors) from marts (business-ready dimensional models).
- **Don't** create wide, denormalized "one big table" models as your primary layer. They are brittle, hard to maintain, and expensive to query.
- **Don't** mix grain in a single fact table. A table with both order-level and line-item-level rows is a bug.
- **Don't** put business logic in dimension surrogate key generation. Surrogate keys are meaningless integers.
- **Don't** skip the staging layer. Transforming source data directly into dimensional models couples your warehouse to source schemas.
- **Don't** use natural keys as join keys in fact tables. Natural keys change; surrogate keys don't.

---

## Common Pitfalls

1. **Undefined grain.** When the grain is ambiguous, aggregations produce wrong results and users lose trust. State the grain in the model documentation and enforce it with unique tests.
2. **Fan-out joins.** Joining a fact table to a dimension at the wrong grain multiplies rows. Always verify join cardinality is many-to-one (fact to dimension).
3. **Missing date dimension.** Computing `EXTRACT(month FROM order_date)` in every query is slower and inconsistent compared to joining `dim_date`.
4. **SCD Type 2 without valid_from/valid_to.** Implementing SCD2 with only a `current_flag` makes point-in-time queries impossible. Always include date range columns.
5. **Conformed dimension divergence.** Two teams build separate `dim_customer` tables with different logic. Establish a single owner for each conformed dimension.
6. **Over-modeling.** Creating dimensions for every possible attribute before anyone needs them wastes effort. Model what the business queries today; extend when needed.

---

## Checklist

- [ ] Every fact table has an explicitly documented grain
- [ ] Fact tables use surrogate keys to join dimensions, not natural keys
- [ ] Conformed dimensions are shared across fact tables
- [ ] SCD Type 2 dimensions include `valid_from`, `valid_to`, and `is_current` columns
- [ ] A `dim_date` table exists with fiscal periods and holidays
- [ ] Staging models are separated from dimensional marts
- [ ] Naming conventions are consistent (`fct_`, `dim_`, `stg_` prefixes)
- [ ] Join cardinality (many-to-one) is verified between facts and dimensions
- [ ] No mixed grain in any single fact table
- [ ] Model documentation includes grain, source, and update frequency
