---
name: format
description: "Format Go sources."
---

# /format Command

Format Go sources.

## Usage

```
/format
```

Runs:

```
gofmt -w .
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
