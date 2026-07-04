# Mobile Implementation Plan: [Feature / Story Title]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Developer name]               |
| Related links | [Story / issue / design spec links] |
| Status        | Draft / Reviewed / Approved    |

*Step-by-step plan for implementing a mobile feature. Write this before coding to surface platform-specific unknowns early and align with reviewers.*

---

## Story Reference

- **Story/Issue:** [Link or ID]
- **Acceptance criteria summary:** [Brief restatement of what "done" looks like from the story]

---

## Platform Scope

| Platform       | In Scope? | Notes                                       |
|----------------|-----------|---------------------------------------------|
| iOS (Swift)    | [Yes/No]  | [Min OS version, target devices]            |
| Android (Kotlin) | [Yes/No] | [Min API level, target devices]            |
| Cross-Platform | [Yes/No]  | [Framework: React Native / Flutter / etc.]  |

---

## Approach Summary

*One to three sentences describing the overall implementation strategy.*

[Describe the high-level approach: what pattern or technique you will use, why this approach was chosen, and how it addresses mobile-specific concerns (offline, performance, platform conventions).]

---

## Implementation Steps

| Step | Description                                      | Platform  | Estimated Effort |
|------|--------------------------------------------------|-----------|------------------|
| 1    | [e.g., Define local data model and storage schema] | [Shared] | [e.g., 2h]     |
| 2    | [e.g., Implement offline-first data layer]       | [Shared]  | [e.g., 4h]      |
| 3    | [e.g., Build UI components]                      | [iOS/Android/Both] | [e.g., 3h] |
| 4    | [e.g., Integrate with backend API]               | [Shared]  | [e.g., 2h]      |
| 5    | [e.g., Add sync conflict resolution]             | [Shared]  | [e.g., 2h]      |
| 6    | [e.g., Write unit, widget, and integration tests] | [Both]   | [e.g., 3h]      |
| 7    | [e.g., Device testing across matrix]             | [Both]    | [e.g., 2h]      |

---

## Files to Modify or Create

| File Path                  | Change Type (New / Modify / Delete) | Purpose                     |
|----------------------------|-------------------------------------|-----------------------------|
| [src/models/resource.swift] | [New]                              | [Data model definition]     |
| [src/services/sync.swift]  | [New]                               | [Offline sync logic]        |
| [src/views/resource.swift] | [New]                               | [UI component]              |
| [tests/test_resource.swift] | [New]                              | [Unit and widget tests]     |

---

## Offline Strategy

*How will the feature work without network connectivity?*

- **Local storage:** [What data is stored locally and how (SQLite, Core Data, Room, AsyncStorage)]
- **Sync approach:** [How data syncs when connectivity returns (last-write-wins, merge, queue)]
- **Conflict resolution:** [How conflicts between local and remote data are handled]
- **User feedback:** [How the user knows they are offline and what limitations exist]

---

## Testing Approach

- **Unit tests:** [What logic will be unit tested and key edge cases]
- **Widget/UI tests:** [What components will have widget tests and key states]
- **Integration tests:** [What interactions will be tested end to end]
- **Device testing:** [Which devices and OS versions will be tested]
- **Manual verification:** [Any manual steps needed]

---

## Risks and Unknowns

| Risk / Unknown                        | Impact  | Mitigation or Plan to Resolve         |
|---------------------------------------|---------|---------------------------------------|
| [e.g., API not yet available for offline sync] | [High] | [Use mock API; integrate when ready] |
| [e.g., Low-end device performance unknown]     | [Medium] | [Profile on target device early]   |
| [e.g., Platform API deprecation in next OS]    | [Low]    | [Track deprecation timeline]       |

---

## Dependencies

- [ ] [e.g., Backend API endpoint must be deployed]
- [ ] [e.g., UI designs approved for both platforms]
- [ ] [e.g., Signing certificates and provisioning profiles configured]

---

## Definition of Done

- [ ] All implementation steps are complete
- [ ] Unit, widget, and integration tests pass on both platforms
- [ ] Code reviewed and approved
- [ ] Acceptance criteria from the story are met
- [ ] Device testing matrix completed
- [ ] Offline scenarios verified
- [ ] No known regressions introduced
