---
name: dev
description: "Load the package for interactive development."
---

# /dev Command

Load the package for interactive development.

## Usage

```
/dev
```

Runs:

```
Rscript -e "devtools::load_all()"
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
