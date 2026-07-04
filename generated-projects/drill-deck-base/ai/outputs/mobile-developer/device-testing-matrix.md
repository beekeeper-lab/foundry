# Device Testing Matrix: [Feature / Release Title]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Developer name]               |
| Related links | [Story / issue / PR links]     |
| Status        | Draft / Reviewed / Approved    |

*Record of device testing results across the supported matrix. Fill in as you test each device/OS combination.*

---

## Target Matrix

### iOS

| Device            | OS Version | Status     | Notes                       |
|-------------------|------------|------------|-----------------------------|
| [e.g., iPhone 16] | [e.g., 18.x] | [Pass/Fail/Skip] | [Any observations]   |
| [e.g., iPhone SE] | [e.g., 16.x] | [Pass/Fail/Skip] | [Any observations]   |
| [e.g., iPad Air]  | [e.g., 17.x] | [Pass/Fail/Skip] | [Any observations]   |

### Android

| Device                  | OS Version | Status     | Notes                       |
|-------------------------|------------|------------|-----------------------------|
| [e.g., Pixel 8]        | [e.g., 14] | [Pass/Fail/Skip] | [Any observations]   |
| [e.g., Samsung A14]    | [e.g., 13] | [Pass/Fail/Skip] | [Any observations]   |
| [e.g., Pixel Tablet]   | [e.g., 14] | [Pass/Fail/Skip] | [Any observations]   |

---

## Performance Observations

| Metric         | Device          | Value         | Acceptable? |
|----------------|-----------------|---------------|-------------|
| Startup time   | [High-end]      | [e.g., 1.2s]  | [Yes/No]   |
| Startup time   | [Low-end]       | [e.g., 3.4s]  | [Yes/No]   |
| Memory usage   | [High-end]      | [e.g., 85MB]  | [Yes/No]   |
| Memory usage   | [Low-end]       | [e.g., 62MB]  | [Yes/No]   |
| Battery impact | [Test device]   | [e.g., 2%/hr] | [Yes/No]   |

---

## Offline Testing

| Scenario                              | Result     | Notes                    |
|---------------------------------------|------------|--------------------------|
| App launch without connectivity       | [Pass/Fail] | [Observations]          |
| Lose connectivity during data sync    | [Pass/Fail] | [Observations]          |
| Regain connectivity after offline use | [Pass/Fail] | [Observations]          |
| Airplane mode toggle                  | [Pass/Fail] | [Observations]          |

---

## Device-Specific Issues

| # | Device / OS       | Issue Description              | Severity | Reproduction Steps        |
|---|-------------------|--------------------------------|----------|---------------------------|
| 1 | [Device, OS ver]  | [What goes wrong]             | [H/M/L]  | [Steps to reproduce]      |

---

## Definition of Done

- [ ] At least one high-end and one low-end device tested per platform
- [ ] Minimum supported OS version and latest OS version covered
- [ ] Performance metrics recorded and within acceptable range
- [ ] Offline scenarios tested
- [ ] Device-specific issues documented with reproduction steps
- [ ] All critical and high severity issues resolved before release
