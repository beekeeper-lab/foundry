---
name: build
description: "Build the Flutter app (debug)."
---

# /build Command

Build the Flutter app (debug).

## Usage

```
/build
```

Runs:

```
flutter build apk --debug 2>/dev/null || flutter build
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
