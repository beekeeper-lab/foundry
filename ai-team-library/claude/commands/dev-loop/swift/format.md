---
name: format
description: "Format (swift-format when available)."
---

# /format Command

Format (swift-format when available).

## Usage

```
/format
```

Runs:

```
swift-format -i -r Sources Tests 2>/dev/null || echo 'swift-format not installed'
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
