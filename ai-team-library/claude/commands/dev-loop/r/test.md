---
name: test
description: "Run the R test suite."
---

# /test Command

Run the R test suite.

## Usage

```
/test
```

Runs:

```
Rscript -e "devtools::test()"
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
