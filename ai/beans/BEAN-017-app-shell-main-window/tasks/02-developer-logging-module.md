# Task 02: Logging Module

| Field | Value |
|-------|-------|
| **Owner** | developer |
| **Depends On** | — |
| **Status** | Pending |

## Goal

Create `foundry_app/core/logging_config.py` — structured logging with rotating file handler.

## Inputs

- Python logging module, RotatingFileHandler

## Definition of Done

- [ ] `setup_logging()` configures root logger
- [ ] Rotating file handler (5 MB, 3 backups)
- [ ] Console handler for development
- [ ] Log file written to platform-appropriate location
