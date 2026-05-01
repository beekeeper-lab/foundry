# Database Capacity Planning Report

| Field | Value |
|-------|-------|
| **Report ID** | CAP-NNN |
| **Date** | YYYY-MM-DD |
| **Author** | Database Administrator |
| **Database** | _Database name and engine_ |
| **Reporting Period** | _e.g., Q1 2026_ |

## Current State

### Storage

| Database / Schema | Current Size | Growth Rate | Projected 6-Month | Projected 12-Month |
|-------------------|-------------|-------------|-------------------|-------------------|
| _name_ | _GB_ | _GB/month_ | _GB_ | _GB_ |

### Performance

| Metric | Current | Trend | Threshold |
|--------|---------|-------|-----------|
| Avg query latency | _ms_ | _↑ / ↓ / →_ | _ms_ |
| P95 query latency | _ms_ | _↑ / ↓ / →_ | _ms_ |
| Connections (peak) | _count_ | _↑ / ↓ / →_ | _max pool_ |
| Lock wait time | _ms_ | _↑ / ↓ / →_ | _ms_ |
| Cache hit ratio | _%_ | _↑ / ↓ / →_ | _min %_ |

### Top Tables by Size

| Table | Row Count | Size | Growth Rate |
|-------|-----------|------|-------------|
| _table_ | _count_ | _GB_ | _rows/day_ |

## Projections

_Based on current growth rates, when will resource thresholds be reached?_

| Resource | Current Usage | Capacity | Time to Threshold |
|----------|-------------|----------|-------------------|
| Storage | _%_ | _GB_ | _months_ |
| Connections | _%_ | _max_ | _months_ |
| IOPS | _%_ | _max_ | _months_ |
| Memory | _%_ | _GB_ | _months_ |

## Recommendations

### Short-Term (0-3 months)

1. _Recommendation with rationale and estimated impact_

### Medium-Term (3-6 months)

1. _Recommendation with rationale and estimated impact_

### Long-Term (6-12 months)

1. _Recommendation with rationale and estimated impact_

## Scaling Options

| Option | Complexity | Cost Impact | Capacity Gain | Recommendation |
|--------|-----------|-------------|---------------|----------------|
| _Vertical scaling_ | _Low_ | _$$$_ | _2x_ | _Short-term_ |
| _Read replicas_ | _Medium_ | _$$_ | _Read: 3x_ | _Medium-term_ |
| _Sharding_ | _High_ | _$$_ | _Write: Nx_ | _Last resort_ |
