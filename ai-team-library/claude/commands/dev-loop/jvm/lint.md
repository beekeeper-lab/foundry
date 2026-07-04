---
name: lint
description: "Run all verification tasks."
---

# /lint Command

Run all verification tasks.

## Usage

```
/lint
```

Runs:

```
./gradlew check
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
