---
name: lint
description: "Lint Go code (golangci-lint when available, else go vet)."
---

# /lint Command

Lint Go code (golangci-lint when available, else go vet).

## Usage

```
/lint
```

Runs:

```
golangci-lint run 2>/dev/null || go vet ./...
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
