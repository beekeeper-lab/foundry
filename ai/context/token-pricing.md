# Token Pricing

Cost-per-token rates for estimating bean and task costs from telemetry data.
Update this file when Anthropic changes pricing.

| Field | Value |
|-------|-------|
| **Model** | Claude Opus 4 |
| **Input Rate** | $0.000015 per token ($15/MTok) |
| **Output Rate** | $0.000075 per token ($75/MTok) |
| **Updated** | 2026-02-16 |

## Usage

Cost is computed as: `cost = (tokens_in × input_rate) + (tokens_out × output_rate)`

The `/telemetry-report` skill and `telemetry-stamp.py` hook both read rates from this file.
