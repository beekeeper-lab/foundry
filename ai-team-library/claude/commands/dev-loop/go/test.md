---
name: test
description: "Run the Go test suite."
---

# /test Command

Run the Go test suite.

## Usage

```
/test
```

Runs:

```
go test ./...
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
