---
name: lint
description: "Lint (swiftlint when available)."
---

# /lint Command

Lint (swiftlint when available).

## Usage

```
/lint
```

Runs:

```
swiftlint 2>/dev/null || echo 'swiftlint not installed'
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
