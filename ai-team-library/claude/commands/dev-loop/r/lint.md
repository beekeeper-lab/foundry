---
name: lint
description: "Lint R sources."
---

# /lint Command

Lint R sources.

## Usage

```
/lint
```

Runs:

```
Rscript -e "lintr::lint_package()"
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
