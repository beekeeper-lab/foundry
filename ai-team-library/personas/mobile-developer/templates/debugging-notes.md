# Mobile Debugging Notes: [Issue Title or Symptom]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Developer name]               |
| Related links | [Issue / incident / PR links]  |
| Status        | Draft / Reviewed / Approved    |

*Structured record of a mobile debugging investigation. Fill this in as you investigate so the reasoning is preserved for future reference.*

---

## Issue Reference

- **Issue / Incident:** [Link or ID]
- **Reported by:** [Name or team]
- **Severity:** [Critical / High / Medium / Low]
- **Summary:** [One sentence description of the observed problem]

---

## Affected Platform(s)

| Platform | Affected? | Version(s)                |
|----------|-----------|---------------------------|
| iOS      | [Yes/No]  | [e.g., 16.x and above]   |
| Android  | [Yes/No]  | [e.g., API 30+]          |

---

## Reproduction Steps

*Exact steps to reproduce the issue consistently.*

1. [Step 1: e.g., "Launch app on iPhone SE running iOS 16.4"]
2. [Step 2: e.g., "Navigate to profile screen"]
3. [Step 3: e.g., "Toggle airplane mode and tap refresh -- observe crash"]

**Reproducibility:** [Always / Intermittent / Once only]
**Device(s) Tested:** [List specific devices and OS versions where reproduction was attempted]

---

## Environment Details

| Attribute          | Value                                |
|--------------------|--------------------------------------|
| Device             | [e.g., iPhone SE 3rd gen, Pixel 7a]  |
| OS version         | [e.g., iOS 16.4, Android 14]        |
| App version        | [e.g., v2.3.1 / build 456]          |
| Network state      | [e.g., WiFi / cellular / airplane mode] |
| Relevant config    | [e.g., feature flags, build variant] |

---

## Crash / Error Details

*Include stack traces, crash logs, or error output.*

```
[Paste relevant crash log, stack trace, or ANR trace here]
```

**Crash reporting tool:** [e.g., Crashlytics, Sentry -- include link to report if available]

---

## Hypotheses

*List candidate root causes before testing them.*

1. [e.g., "Force unwrap on nil optional when API returns empty response"]
2. [e.g., "Race condition between background sync and UI update on main thread"]
3. [e.g., "Memory pressure on low-end device causes OOM during image loading"]

---

## Experiments Conducted

| # | Hypothesis Tested | Experiment / Test Performed             | Result                           |
|---|-------------------|-----------------------------------------|----------------------------------|
| 1 | Hypothesis 1      | [e.g., "Added nil check and tested with empty response"] | [e.g., "Crash no longer occurs -- confirmed"] |
| 2 | Hypothesis 2      | [e.g., "Added thread assertions and logging"] | [e.g., "No thread violations observed -- ruled out"] |

---

## Root Cause

[Clear statement of the confirmed root cause, with evidence from the experiments above. Include which platform(s) and device(s) are affected and why.]

---

## Fix Applied / Proposed

- **Fix description:** [What was changed and why it addresses the root cause]
- **PR / Commit:** [Link to the fix]
- **Verification:** [How the fix was verified, including which devices were tested]
- **Regression test:** [Description of the automated test added to prevent recurrence]

---

## Prevention

*How can we prevent this class of issue from recurring?*

- [ ] [e.g., "Enable strict null safety / optional handling lint rules"]
- [ ] [e.g., "Add integration test for empty API response scenario"]
- [ ] [e.g., "Add memory profiling to CI for low-end device simulation"]
- [ ] [e.g., "Add crash monitoring alert for this error class"]

---

## Lessons Learned

- [e.g., "Our offline fallback does not handle the case where the cache is empty on first launch."]
- [e.g., "We need to test with actual low-end devices, not just simulators configured with low memory."]

---

## Definition of Done

- [ ] Root cause is confirmed with evidence
- [ ] Fix is implemented and verified on affected device(s)
- [ ] Regression test is added
- [ ] Prevention measures are identified and tracked as follow-up tasks
- [ ] Lessons learned are documented and shared with the team
