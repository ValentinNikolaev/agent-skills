# Accessibility Checklist

> Vendored from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills/blob/7676817c12a1317454ae3898a0c5c1eacf5dd3d5/references/accessibility-checklist.md) at commit `7676817c12a1317454ae3898a0c5c1eacf5dd3d5` under the bundled MIT license.
> Repository-specific rules override this snapshot. Treat tool commands and numeric targets as advisory; the main skill's cost and approval gate still applies.

Quick reference for reviewing web UI accessibility. The upstream snapshot targets WCAG 2.1 AA; follow any newer or stricter repository requirement.

## Table of Contents

- [Essential Checks](#essential-checks)
- [Operator workflow and control state](#operator-workflow-and-control-state)
- [Common HTML Patterns](#common-html-patterns)
- [Testing Tools](#testing-tools)
- [Quick Reference: ARIA Live Regions](#quick-reference-aria-live-regions)
- [Common Anti-Patterns](#common-anti-patterns)

## Essential Checks

### Keyboard Navigation
- [ ] All interactive elements focusable via Tab key
- [ ] Focus order follows visual/logical order
- [ ] Focus is visible (outline/ring on focused elements)
- [ ] Custom widgets have keyboard support (Enter to activate, Escape to close)
- [ ] No keyboard traps (user can always Tab away from a component)
- [ ] Skip-to-content link at top of page - visible (at least) on keyboard focus
- [ ] Modals trap focus while open, return focus on close

### Screen Readers
- [ ] All images have `alt` text (or `alt=""` for decorative images)
- [ ] All form inputs have associated labels (`<label>` or `aria-label`)
- [ ] Buttons and links have descriptive text (not "Click here")
- [ ] Icon-only buttons have `aria-label`
- [ ] Page has one `<h1>` and headings don't skip levels
- [ ] Dynamic content changes announced (`aria-live` regions)
- [ ] Tables have `<th>` headers with scope

### Visual
- [ ] Text contrast ≥ 4.5:1 (normal text) or ≥ 3:1 (large text, 18px+)
- [ ] UI components contrast ≥ 3:1 against background
- [ ] Color is not the only way to convey information
- [ ] Text resizable to 200% without breaking layout
- [ ] No content that flashes more than 3 times per second

### Forms
- [ ] Every input has a visible label
- [ ] Required fields indicated (not by color alone)
- [ ] Error messages specific and associated with the field
- [ ] Every disabled save/submit action has an on-screen reason near the relevant field or action, associated with the field via `aria-describedby` (or equivalent accessible semantics). A hidden tooltip or `aria-label` alone is not a visible explanation. No visible reason is a P2 finding even if the plan prescribes it.
- [ ] Validation failures reach visible, field-associated feedback. Trace `catch { return null }` and similar fallbacks to consumers: silently disabling an action after swallowing the error is a finding.
- [ ] Error state visible by more than color (icon, text, border)
- [ ] Form submission errors summarized and focusable
- [ ] Known fields use autocomplete (for example `type="email" autocomplete="email"`)

### Content
- [ ] Language declared (`<html lang="en">`)
- [ ] Page has a descriptive `<title>`
- [ ] Links distinguish from surrounding text (not by color alone)
- [ ] Touch targets ≥ 44x44px on mobile
- [ ] Meaningful empty states (not blank screens)

## Operator workflow and control state

Within the reviewed UI scope, trace the operator's normal, malformed-input, and empty-data paths. Check what the operator can see and do after each transition, not only whether the predicate matches the spec.

- [ ] A Continue/Resume action appears only when there is work to resume, or clearly explains why it is unavailable. It must not offer an empty recovery path.
- [ ] Row actions match the current state: Add must not propose adding an already-added item unless a distinct, meaningful operation is explained. Check pending additions/removals as well as persisted state.
- [ ] Operator-visible lists have an explicit, suitable ordering contract and implementation, such as alphabetical order or a documented business rank. `Object.keys`/insertion order alone does not establish one. Cite the affected search/selection workflow and missing order when reporting it.
- [ ] Errors leave a visible route to correct input, cancel, or retry. A spec-prescribed dead end is a `spec-driven defect`; cite both the spec and the changed UI path rather than dropping the finding.

User-reported event-catalog regression: Save stayed disabled because a parser accepted only `DP-N` issue keys and `catch { return null }` swallowed its error. A different project's key and a board URL containing `?selectedIssue=OTHER-42` silently blocked saving. Trace those inputs and malformed/empty values through parsing, disabled state, and field feedback. Keep the P2 finding even if the plan explicitly selected this behavior. Accepting only one project is a separate contract question; silent blocking is still a defect.

## Common HTML Patterns

### Buttons vs. Links

```html
<!-- Use <button> for actions -->
<button onClick={handleDelete}>Delete Task</button>

<!-- Use <a> for navigation -->
<a href="/tasks/123">View Task</a>

<!-- NEVER use div/span as buttons -->
<div onClick={handleDelete}>Delete</div>  <!-- BAD -->
```

### Form Labels

```html
<!-- Explicit label association -->
<label htmlFor="email">Email address</label>
<input id="email" type="email" required />

<!-- Implicit wrapping -->
<label>
  Email address
  <input type="email" required />
</label>

<!-- Hidden label (visible label preferred) -->
<input type="search" aria-label="Search tasks" />
```

### ARIA Roles

```html
<!-- Navigation -->
<nav aria-label="Main navigation">...</nav>
<nav aria-label="Footer links">...</nav>

<!-- Status messages -->
<div role="status" aria-live="polite">Task saved</div>

<!-- Alert messages -->
<div role="alert">Error: Title is required</div>

<!-- Modal dialogs -->
<dialog aria-modal="true" aria-labelledby="dialog-title">
  <h2 id="dialog-title">Confirm Delete</h2>
  ...
</dialog>

<!-- Loading states -->
<div aria-busy="true" aria-label="Loading tasks">
  <Spinner />
</div>
```

### Accessible Lists

```html
<ul role="list" aria-label="Tasks">
  <li>
    <input type="checkbox" id="task-1" aria-label="Complete: Buy groceries" />
    <label htmlFor="task-1">Buy groceries</label>
  </li>
</ul>
```

## Testing Tools

```bash
# Automated audit
npx axe-core          # Programmatic accessibility testing
npx pa11y             # CLI accessibility checker

# In browser
# Chrome DevTools → Lighthouse → Accessibility
# Chrome DevTools → Elements → Accessibility tree

# Screen reader testing
# macOS: VoiceOver (Cmd + F5)
# Windows: NVDA (free) or JAWS
# Linux: Orca
```

## Quick Reference: ARIA Live Regions

| Value | Behavior | Use For |
|-------|----------|---------|
| `aria-live="polite"` | Announced at next pause | Status updates, saved confirmations |
| `aria-live="assertive"` | Announced immediately | Errors, time-sensitive alerts |
| `role="status"` | Same as `polite` | Status messages |
| `role="alert"` | Same as `assertive` | Error messages |

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| `div` as button | Not focusable, no keyboard support | Use `<button>` |
| Missing `alt` text | Images invisible to screen readers | Add descriptive `alt` |
| Color-only states | Invisible to color-blind users | Add icons, text, or patterns |
| Autoplaying media | Disorienting, can't be stopped | Add controls, don't autoplay |
| Custom dropdown with no ARIA | Unusable by keyboard/screen reader | Use native `<select>` or proper ARIA listbox |
| Removing focus outlines | Users can't see where they are | Style outlines, don't remove them |
| Empty links/buttons | "Link" announced with no description | Add text or `aria-label` |
| `tabindex > 0` | Breaks natural tab order | Use `tabindex="0"` or `-1` only |
