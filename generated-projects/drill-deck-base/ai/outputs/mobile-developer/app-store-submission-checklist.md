# App Store Submission Checklist: [App Name] v[Version]

## Metadata

| Field         | Value                          |
|---------------|--------------------------------|
| Date          | YYYY-MM-DD                     |
| Owner         | [Developer name]               |
| Related links | [Release notes / issue links]  |
| Status        | Draft / Reviewed / Approved    |

*Pre-submission checklist for Apple App Store and Google Play Store releases. Complete all applicable items before submitting.*

---

## Build Verification

- [ ] Build compiles without warnings on release configuration
- [ ] All unit, widget, and integration tests pass
- [ ] No debug flags, test endpoints, or development configurations remain
- [ ] Version number and build number are incremented correctly
- [ ] Signing certificates and provisioning profiles are valid and not expiring soon

### iOS Specific

- [ ] Archive builds successfully in Xcode
- [ ] IPA passes Xcode validation checks
- [ ] Minimum deployment target is correct
- [ ] No private API usage detected

### Android Specific

- [ ] AAB/APK is signed with release keystore
- [ ] ProGuard/R8 rules are correct -- no runtime crashes from obfuscation
- [ ] Target SDK version meets Play Store requirements
- [ ] 64-bit support is included

---

## App Store Metadata

### iOS (App Store Connect)

- [ ] App description is current
- [ ] Keywords are updated
- [ ] Screenshots are current for all required device sizes
- [ ] What's New text describes changes in this version
- [ ] Privacy policy URL is valid
- [ ] App privacy nutrition labels are accurate

### Android (Google Play Console)

- [ ] Store listing description is current
- [ ] Screenshots are current for phone and tablet
- [ ] Release notes describe changes in this version
- [ ] Privacy policy URL is valid
- [ ] Data safety section is accurate
- [ ] Content rating questionnaire is current

---

## Permissions and Capabilities

| Permission / Capability | Platform | New in this release? | Justification              |
|-------------------------|----------|----------------------|----------------------------|
| [e.g., Camera]          | [Both]   | [Yes/No]             | [Why the app needs this]   |
| [e.g., Location]        | [iOS]    | [Yes/No]             | [Why the app needs this]   |

- [ ] All permissions have user-facing justification strings
- [ ] No unnecessary permissions are requested
- [ ] New permissions are documented in release notes

---

## Compliance

- [ ] No undeclared data collection or tracking
- [ ] GDPR/CCPA consent flows are implemented where required
- [ ] Age rating is appropriate for content
- [ ] Export compliance documentation is current (encryption usage)
- [ ] Third-party SDK licenses are documented and compliant

---

## Testing Sign-Off

- [ ] Device testing matrix completed and passed
- [ ] Offline scenarios verified
- [ ] Performance metrics within acceptable range
- [ ] Accessibility audit passed (VoiceOver/TalkBack)
- [ ] No critical or high severity bugs outstanding

---

## Definition of Done

- [ ] All checklist items above are completed or marked N/A with justification
- [ ] Build artifact is uploaded to the respective store
- [ ] Release notes are finalized
- [ ] Team Lead has approved the release
- [ ] Rollback plan is documented
