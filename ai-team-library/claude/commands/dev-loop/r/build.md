---
name: build
description: "Build/install the R package."
---

# /build Command

Build/install the R package.

## Usage

```
/build
```

Runs:

```
R CMD INSTALL .
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
