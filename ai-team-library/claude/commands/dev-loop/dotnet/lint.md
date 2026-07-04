---
name: lint
description: "Verify formatting/analyzers without changing files."
---

# /lint Command

Verify formatting/analyzers without changing files.

## Usage

```
/lint
```

Runs:

```
dotnet format --verify-no-changes
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
