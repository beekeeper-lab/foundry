# Token Pricing

Cost-per-token rates for estimating bean and task costs from telemetry data.
Update this file when Anthropic changes pricing.

| Field | Value |
|-------|-------|
| **Model** | Claude Opus 4 |
| **Input Rate** | $0.000015 per token ($15/MTok) |
| **Cache Creation Rate** | $0.00001875 per token ($18.75/MTok) |
| **Cache Read Rate** | $0.0000015 per token ($1.50/MTok) |
| **Output Rate** | $0.000075 per token ($75/MTok) |
| **Updated** | 2026-02-17 |

## Usage

Cost is computed as:
```
cost = (input × input_rate) + (cache_creation × cache_creation_rate)
     + (cache_read × cache_read_rate) + (output × output_rate)
```

The JSONL usage object has three input token fields:
- `input_tokens` — non-cached input (charged at Input Rate)
- `cache_creation_input_tokens` — tokens written to prompt cache (charged at Cache Creation Rate)
- `cache_read_input_tokens` — tokens read from prompt cache (charged at Cache Read Rate)

Total input tokens = sum of all three. The `/telemetry-report` skill and `telemetry-stamp.py` hook both read rates from this file.
