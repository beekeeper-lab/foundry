---
name: format
description: "Apply formatting (spotless when configured)."
---

# /format Command

Apply formatting (spotless when configured).

## Usage

```
/format
```

Runs:

```
./gradlew spotlessApply 2>/dev/null || echo 'no spotless task configured'
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
