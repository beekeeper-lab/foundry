---
name: build
description: "Build via the Gradle wrapper."
---

# /build Command

Build via the Gradle wrapper.

## Usage

```
/build
```

Runs:

```
./gradlew build -x test
```

Report the full output. On failure, summarize the first actionable error
and stop — do not retry blindly.
