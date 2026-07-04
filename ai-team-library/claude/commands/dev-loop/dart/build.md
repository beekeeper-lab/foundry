---
name: build
description: "Compile the Dart project."
---

# /build Command

Compile the Dart project.

## Usage

```
/build
```

Runs:

```
dart compile exe bin/main.dart 2>/dev/null || dart pub get
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
