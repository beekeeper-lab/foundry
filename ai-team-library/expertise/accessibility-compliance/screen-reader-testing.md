# Screen Reader Testing

Standards for testing web applications with screen readers to validate that content is
perceivable, operable, and understandable for users who rely on assistive technology. Manual
screen reader testing is required — automated tools cannot verify the quality of the screen
reader experience.

---

## Defaults

| Area | Default | Alternatives |
|------|---------|--------------|
| **Primary screen reader** | NVDA + Firefox (Windows) | JAWS + Chrome, VoiceOver + Safari (macOS/iOS), TalkBack + Chrome (Android) |
| **Testing matrix** | NVDA/Firefox + VoiceOver/Safari | Full matrix per WebAIM Screen Reader Survey |
| **Testing frequency** | Every sprint for changed UI components | Pre-release only (not recommended), continuous |
| **Test documentation** | Screen reader test script per feature | Recorded test sessions, annotated screenshots |

---

## Screen Reader Market Share

| Screen Reader | Platform | Market Share | Best Browser Pairing |
|---------------|----------|-------------|---------------------|
| JAWS | Windows | ~40% | Chrome, Edge |
| NVDA | Windows | ~30% | Firefox, Chrome |
| VoiceOver | macOS/iOS | ~20% | Safari |
| TalkBack | Android | ~5% | Chrome |
| Narrator | Windows | ~3% | Edge |

Test with at least two screen readers from different platforms to catch implementation
differences.

---

## Do / Don't

- **Do** test with the screen reader's recommended browser pairing — NVDA with Firefox,
  VoiceOver with Safari, JAWS with Chrome.
- **Do** create screen reader test scripts that specify the expected announcement for each
  interactive element and landmark.
- **Do** test the full user journey, not just individual components — navigation, form
  submission, error recovery, success confirmation.
- **Do** verify that dynamic content changes are announced via `aria-live` regions.
- **Do** test with screen reader in both browse mode (reading) and focus/forms mode
  (interacting) — behavior differs significantly.
- **Don't** assume that passing automated tests means the screen reader experience is good —
  automated tools test code, not user experience.
- **Don't** test only with VoiceOver on macOS — it is the most forgiving screen reader and
  may mask issues that NVDA and JAWS expose.
- **Don't** add excessive `aria-label` attributes that duplicate visible text — screen reader
  users hear everything twice.
- **Don't** use `title` attributes as the primary accessible name — most screen readers do
  not reliably announce them.

---

## Common Pitfalls

1. **Testing only in browse mode.** Screen readers have distinct modes: browse mode for
   reading content and forms/focus mode for interacting with widgets. Custom widgets may work
   in one mode but not the other. Test both modes explicitly.

2. **Verbose or confusing announcements.** A button announced as "Close button close dialog
   button" indicates redundant ARIA labeling. Listen to the actual output and simplify.
   Remove `aria-label` when the visible text is sufficient.

3. **Missing announcements for dynamic updates.** AJAX-loaded content, toast notifications,
   and form validation errors may appear visually but go unannounced. Verify that `aria-live`
   regions or `role="alert"` trigger announcements.

4. **Testing with a single screen reader.** NVDA, JAWS, and VoiceOver interpret ARIA
   differently. A combobox that works in VoiceOver may be unusable in JAWS. Test with at
   least two screen readers before release.

5. **Images of text without alt text.** Logos, headings rendered as images, and infographics
   must have meaningful `alt` text. An empty `alt=""` is correct only for purely decorative
   images that add no information.

---

## Screen Reader Test Script Template

```markdown
## Feature: User Login Form

### Setup
1. Navigate to /login
2. Enable screen reader (NVDA: Ctrl+Alt+N, VoiceOver: Cmd+F5)

### Test Steps

| # | Action | Expected Announcement |
|---|--------|-----------------------|
| 1 | Tab to email field | "Email, edit text, required" |
| 2 | Type email address | Characters echoed as typed |
| 3 | Tab to password field | "Password, password edit text, required" |
| 4 | Tab to "Remember me" checkbox | "Remember me, checkbox, not checked" |
| 5 | Press Space to check | "checked" |
| 6 | Tab to "Sign in" button | "Sign in, button" |
| 7 | Press Enter to submit | (loading state announced, then result) |
| 8 | Invalid credentials submitted | "Error: Invalid email or password, alert" |
| 9 | Tab to error message | "Error: Invalid email or password" |

### Landmarks
- Page has banner, navigation, main, and contentinfo landmarks
- "Skip to main content" link is first focusable element
- Form is within main landmark

### Headings
- H1: "Sign in to your account"
- Heading hierarchy is sequential (no skipped levels)
```

---

## NVDA Quick Reference

```
# Starting / Stopping
Ctrl + Alt + N          Start NVDA
Insert + Q              Quit NVDA

# Navigation
Insert + F7             Elements list (links, headings, landmarks)
H / Shift + H           Next / previous heading
D / Shift + D           Next / previous landmark
K / Shift + K           Next / previous link
F / Shift + F           Next / previous form field
T / Shift + T           Next / previous table

# Reading
Insert + Down Arrow     Read from current position
Ctrl                    Stop reading
Insert + Up Arrow       Read current line
Insert + F              Read current field info

# Modes
Insert + Space          Toggle browse / focus mode
```

---

## VoiceOver Quick Reference

```
# Starting / Stopping
Cmd + F5                Toggle VoiceOver on/off
VO = Ctrl + Option      VoiceOver modifier key

# Navigation
VO + U                  Open rotor (navigate by headings, links, landmarks)
VO + Right/Left         Move to next/previous element
VO + Shift + Down       Enter a group (table, list, landmark)
VO + Shift + Up         Exit a group

# Reading
VO + A                  Read from current position
Ctrl                    Stop reading
VO + B                  Read from top

# Interaction
VO + Space              Activate (click) current element
VO + Shift + M          Open shortcut menu
```

---

## Alternatives

| Tool | When to consider |
|------|-----------------|
| JAWS (Freedom Scientific) | Enterprise standard, deepest Office/PDF support, commercial license |
| NVDA (NV Access) | Free, open-source, strong web support, best for developer testing |
| VoiceOver (Apple) | Built into macOS/iOS, required for Safari/iOS testing |
| TalkBack (Google) | Built into Android, required for Android app testing |
| Narrator (Microsoft) | Built into Windows, paired with Edge |
| ChromeVox | Chrome extension, useful for quick Chromebook testing |

---

## Checklist

- [ ] Screen reader testing performed with at least two screen readers (NVDA + VoiceOver recommended)
- [ ] Test scripts document expected announcements for all interactive elements
- [ ] Full user journeys tested, not just individual components
- [ ] Dynamic content updates verified as announced (aria-live, role="alert")
- [ ] Browse mode and focus/forms mode tested separately
- [ ] Heading hierarchy is logical and sequential (no skipped levels)
- [ ] All landmarks announced and navigable (banner, nav, main, contentinfo)
- [ ] Images have meaningful alt text (or empty alt for decorative images)
- [ ] Form fields have associated labels announced correctly
- [ ] Error messages announced immediately upon display
