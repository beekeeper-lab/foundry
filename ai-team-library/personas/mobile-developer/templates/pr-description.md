# PR: [Short descriptive title]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Author name]                  |
| Related links | [Issue / story / design links] |
| Status        | Draft / Ready for Review       |

---

## Summary

*What does this PR do and why?*

[One to three sentences explaining the change. Focus on the "why" -- the problem being solved or the feature being delivered -- not just the "what."]

---

## Changes Made

- [Change 1: e.g., "Added offline caching for user profile using Room with 24-hour TTL"]
- [Change 2: e.g., "Implemented pull-to-refresh with conflict resolution"]
- [Change 3: e.g., "Added unit tests for sync logic and widget tests for profile view"]
- [Change 4: e.g., "Updated permissions manifest for background sync"]

---

## Platform Notes

| Concern              | iOS                              | Android                          |
|----------------------|----------------------------------|----------------------------------|
| Navigation           | [e.g., UINavigationController]   | [e.g., Jetpack Navigation]      |
| Local storage        | [e.g., Core Data]                | [e.g., Room]                    |
| Background sync      | [e.g., BGTaskScheduler]          | [e.g., WorkManager]             |
| Platform-specific UI | [e.g., swipe-to-delete]          | [e.g., FAB for add action]      |

---

## Testing Done

### Automated

- [ ] Unit tests added/updated -- [brief description of coverage]
- [ ] Widget/UI tests added/updated -- [brief description of scope]
- [ ] Integration tests added/updated -- [brief description of scope]
- [ ] All existing tests pass on both platforms

### Device Testing

- [ ] iOS high-end: [device, OS version] -- [Pass/Fail]
- [ ] iOS low-end: [device, OS version] -- [Pass/Fail]
- [ ] Android high-end: [device, OS version] -- [Pass/Fail]
- [ ] Android low-end: [device, OS version] -- [Pass/Fail]

### Manual

- [ ] [Manual test 1: e.g., "Verified offline behavior -- app displays cached data"]
- [ ] [Manual test 2: e.g., "Confirmed sync resumes when connectivity returns"]

---

## Offline Behavior

- [ ] App functions correctly without connectivity
- [ ] Data is persisted locally and survives app restart
- [ ] Sync resumes correctly when connectivity returns
- [ ] User is informed of offline state

---

## Permissions

*List any new permissions added or modified in this PR.*

| Permission                | Platform | Justification                      |
|---------------------------|----------|------------------------------------|
| [e.g., INTERNET]          | [Android] | [Required for API communication] |
| [e.g., NSLocationWhenInUseUsageDescription] | [iOS] | [Required for location feature] |

---

## Screenshots / Recordings

*Include if this PR changes UI behavior. Remove this section if not applicable.*

| Platform | Before | After |
|----------|--------|-------|
| iOS      | [screenshot or description] | [screenshot or description] |
| Android  | [screenshot or description] | [screenshot or description] |

---

## Risks and Rollback Plan

- **Risk:** [e.g., "New background sync may increase battery usage on older devices"]
- **Rollback:** [e.g., "Revert this PR and disable sync feature flag"]
- **Feature flag:** [e.g., "Behind flag `enable_offline_sync` -- can disable without new build"]

---

## Related Issues

- Closes [#issue-number]
- Related to [#issue-number]

---

## Reviewer Checklist

*For the reviewer to complete during review.*

- [ ] Changes match the PR summary and related issue
- [ ] Code is readable and follows project conventions
- [ ] Platform conventions are respected (HIG for iOS, Material for Android)
- [ ] Tests cover the primary path and key edge cases
- [ ] Offline behavior is handled gracefully
- [ ] No secrets, credentials, or sensitive data included
- [ ] Permissions are justified and requested at point of use
- [ ] Error handling is appropriate and does not leak internals
- [ ] Binary size impact is acceptable
