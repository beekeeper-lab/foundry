---
name: format
description: "Style R sources."
---

# /format Command

Style R sources.

## Usage

```
/format
```

Runs:

```
Rscript -e "styler::style_pkg()"
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
