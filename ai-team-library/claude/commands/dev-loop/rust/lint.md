---
name: lint
description: "Lint with clippy (warnings as errors)."
---

# /lint Command

Lint with clippy (warnings as errors).

## Usage

```
/lint
```

Runs:

```
cargo clippy -- -D warnings
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
