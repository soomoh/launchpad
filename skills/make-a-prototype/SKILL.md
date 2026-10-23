---
name: make-a-prototype
description: Create a functioning interactive prototype in HTML/CSS/JS with real state, navigation, form validation, loading states, error handling, and persistence, optionally wrapped in a device frame (iOS, Android, macOS window, browser chrome). Use when the user asks for a prototype, mockup, demo, clickable flow, or "make it interactive".
---

# Make a Prototype

Make a prototype that works: clickable, navigable, holding real state and giving
feedback. **A prototype has to respond.** Static screens linked with `<a>` tags
don't qualify; what counts is running the flow through genuine clicks, typing, validation, success, and failure.

## Phase 1: Discovery

Confirm these with the user before building. **The flow**: screens, entry point, and goal state,
laid out as a list. **Fidelity**: hi-fi or mid-fi. **Device frame**: desktop
browser, iOS, Android, macOS window, or none. **Variations**: one flow, or several to compare. **Brand / design system**: always confirm it, and if there is
none, run `launchpad:frontend-aesthetic-direction` first. **Sample data**:
realistic-looking content, never Lorem ipsum.

## Phase 2: Map screens and state

Write the flow down first, then embed it in the file as a comment block that
shows the user the plan:

```
Screens:
  1. Welcome — "Get started" CTA → 2
  2. Email entry — validate format → 3 on valid, inline error on invalid
  3. Profile — name, photo upload → 4
  4. Success — "You're in" → 1 (loop demo)

State:
  - currentScreen: 1
  - email: ""
  - emailError: null
```

## Phase 3: Build screen by screen

Mount every screen in the DOM, either by toggling display or through component
state on one page. Visuals should be hi-fi and follow the design system, using
real components instead of generic boxes. Fill them with believable content:
actual names, product copy, numbers. Each screen gets one primary CTA, with
secondary actions smaller and played down.

### Device frames

Write the frame inline, since it takes only a few lines of CSS. It stays fixed
while the prototype runs inside it.

```css
/* Shared: the viewport the prototype renders into */
.frame__screen { overflow: auto; background: var(--color-bg); }

/* iOS — 390×844, notch via a pseudo-element */
.frame--ios { width: 390px; height: 844px; border-radius: 44px; padding: 12px;
              background: #1A1A1A; position: relative; }
.frame--ios .frame__screen { height: 100%; border-radius: 32px; }
.frame--ios::before { content: ""; position: absolute; top: 12px; left: 50%;
              transform: translateX(-50%); width: 120px; height: 28px;
              background: #1A1A1A; border-radius: 0 0 16px 16px; z-index: 2; }

/* Android — 412×915, squarer corners, punch-hole camera */
.frame--android { width: 412px; height: 915px; border-radius: 28px; padding: 10px;
              background: #1A1A1A; position: relative; }
.frame--android .frame__screen { height: 100%; border-radius: 20px; }
.frame--android::before { content: ""; position: absolute; top: 22px; left: 50%;
              transform: translateX(-50%); width: 10px; height: 10px;
              background: #000; border-radius: 50%; z-index: 2; }

/* macOS window — title bar with traffic lights */
.frame--macos { border-radius: 12px; overflow: hidden; background: #fff;
              box-shadow: 0 20px 60px rgba(0,0,0,.25); }
.frame--macos .frame__bar { height: 38px; background: #E8E8E8; display: flex;
              align-items: center; gap: 8px; padding: 0 14px;
              border-bottom: 1px solid #D5D5D5; }
.frame--macos .frame__dot { width: 12px; height: 12px; border-radius: 50%; }

/* Browser chrome — title bar plus a URL pill */
.frame--browser { border-radius: 10px; overflow: hidden; border: 1px solid #DDD; }
.frame--browser .frame__bar { height: 44px; background: #F1F1F1; display: flex;
              align-items: center; gap: 10px; padding: 0 12px; }
.frame--browser .frame__url { flex: 1; height: 26px; border-radius: 13px;
              background: #fff; border: 1px solid #DDD; font: 12px/26px
              ui-monospace, monospace; color: #666; padding: 0 12px; }
```

Traffic lights: three `.frame__dot` spans in `#FF5F57`, `#FEBC2E`, `#28C840`.

## Phase 4: Wire up interactions

Nothing is left unwired; cover more than the happy path:

- **Navigation.** A primary CTA moves ahead, back steps back, and state carries over between screens.
- **Form validation.** Nothing entered → inline error; bad format → an error
  that is specific and attached to its field; good input → proceed.
- **Loading states.** Async actions show a spinner or similar and lock the button
  so it can't be submitted twice. **Simulate the delay with `setTimeout`**; a fake
  backend is no reason to omit the loading state, because it's part of what's under test.
- **Success and error feedback.** Show a toast, inline confirmation, or page
  transition; an error disappears when resolved and stays attached to its field or action.
- **State changes.** The UI responds instantly to toggling, selecting, and filtering.

## Phase 5: Sub-state and persistence

Make these pieces of sub-state reactive: selection, filter/sort, whether a modal
or dropdown is open (focus enters the modal, Escape closes it), and form values
and errors.

Write to `localStorage` anything that should survive a reload, namely the current
screen, form drafts, and tweak values (see `launchpad:make-tweakable`). Users refresh
mid-iteration all the time.

## Phase 6: Verify

**Run through the whole flow in a browser yourself.** Look for CTAs that
dead-end, forms that skip validation, unclear or unrecoverable errors, async
actions with no feedback, invisible state changes, broken keyboard navigation
(Tab through, Enter to submit, Escape to close), and invisible focus. None should exist.

A behavior you truly can't verify should be called out in the summary, not
reported as working.

## Phase 7: Variations (if requested)

Offer variations as tweaks in a floating panel (`launchpad:make-tweakable`),
side by side on a canvas grid (see `launchpad:generate-variations`), or as
toggles within the prototype. **Never spread out v1.html / v2.html / v3.html;
keep one file holding many variants.**

Wrap up briefly: say which flows work, what is simulated ("submit calls
a setTimeout fake"), and which choices are left to the user.
