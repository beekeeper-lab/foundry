---
name: build
description: "Build all Go packages."
---

# /build Command

Build all Go packages.

## Usage

```
/build
```

Runs:

```
go build ./...
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
