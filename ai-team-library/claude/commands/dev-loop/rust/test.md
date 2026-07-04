---
name: test
description: "Run the Rust test suite."
---

# /test Command

Run the Rust test suite.

## Usage

```
/test
```

Runs:

```
cargo test
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
