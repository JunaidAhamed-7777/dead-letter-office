---
version: alpha
name: "Dead Letter Office"
description: "An ink-plum reading desk for a fictional archive, with a parchment sheet that makes evidence tangible."
colors:
  ink: "#211c29"
  desk: "#2b2433"
  desk-hover: "#393042"
  paper: "#e5dac9"
  paper-light: "#eee5d8"
  paper-ink: "#352d38"
  paper-muted: "#645761"
  lavender: "#ccbddc"
  muted: "#b4a7bd"
  line: "#504458"
  paper-line: "#bdb0a1"
  sage: "#a9bcb0"
  warning: "#eccb9c"
  error: "#f4b5b1"
  focus: "#efd39e"
  scroll-thumb: "#796780"
  scroll-track: "#211c29"
  scroll-hover: "#b4a7bd"
  scroll-active: "#ccbddc"
typography:
  serif:
    fontFamily: "Georgia, 'Times New Roman', serif"
  sans:
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
  mono:
    fontFamily: "'Courier New', Courier, monospace"
rounded:
  DEFAULT: "5px"
  dialog: "7px"
spacing:
  page-max: "1240px"
  desk-gap: "42px"
  paper-inset: "32px"
components:
  button:
    minHeight: "35px"
  question:
    minHeight: "140px"
  paper:
    minHeight: "588px"
  dialog:
    maxWidth: "680px"
---

# Dead Letter Office design system

## Overview

### Creative North Star

A small post-office reading room after closing time: plum-painted drawers, faded ledger labels, and an actual sheet of evidence on the desk. The one expressive device is the parchment findings sheet, with a folder tab and an unopened envelope in its empty state. The machine stays out of the way of the letters.

### Product context and register

- **Audience and primary job:** A reader asks a question about fictional letters and verifies the returned quotations against their sources.
- **Product source:** The current project brief specifies a private local archive, original fictional letters, real local semantic retrieval, citations, explicit uncertainty, and no impersonation.
- **Market and locale:** English-language demo, no geographic market assumption. English UI, Gregorian source dates; date-only values format in UTC to avoid calendar-day drift.
- **Usage scene:** A desktop reading desk that becomes a vertically ordered notebook on a phone. No hurried chat stream or infinite feed.
- **Register:** Product/tool, with a literary front door. Clarity and the evidence chain win over atmosphere.
- **Memorable signature:** One physical-looking findings sheet, not a grid of AI cards.
- **Restraint:** Controls, error states, and model limitations use plain language. There is no chatbot avatar, typing theatre, or claim that the system can speak for the dead.
- **Anti-references:** Neon haunted-house games, black-and-lime AI dashboards, generic gradients, cream marketing pages with oversized statistics, faux handwriting as body text.
- **Token ownership/runtime mapping:** `web/style.css :root` is the runtime source of truth. Frontmatter mirrors the same named tokens (`colors.ink` → `--ink`, and so on). This file and CSS must change together. No framework adapter or generated token layer exists. Local decorative envelope paper shades are intentionally illustration-only, not component/state tokens.

## Colors

Ink and desk form the room, lavender supports legible controls, and paper/paper-ink form the evidence surface. Muted text remains readable, never used as a reason to hide a caveat. Sage identifies the local archive. Warning and error colors must be accompanied by text. Focus has a visible warm outline on dark surfaces; paper surfaces use a dark plum outline. A single dark-room theme is intentional; the document itself remains light. Forced colors restore system-operable outlines and remove the decorative envelope.

## Typography

Georgia is used for the title, letter text, and quotations; system sans for actions and explanations; Courier for catalogue metadata. No font is fetched. Display type is large but short, while evidence stays at a readable 16–17px with generous line height. Source headings and queries wrap without truncation. Uppercase is reserved for short archival metadata, never paragraphs. Letter excerpts are explicitly previews; the full text remains reachable.

## Layout

The 1240px desk uses a narrow question rail and a broad evidence sheet, separated by 42px. Below 720px, the inquiry precedes the results in normal document flow. The app never locks the page into a viewport-height dashboard. The catalogue is a bounded render-all collection supplied by the local API, with three, two, then one column as width shrinks. Header navigation wraps rather than clipping. A 32px paper inset becomes 19–23px on mobile. Footer, buttons, validation region, and model-loading area reserve space to reduce jumps.

## Elevation & Depth

The findings sheet has a slight stacked-paper shadow. Catalogue cards are flat. Native modal dialogs have one deep shadow and a dark backdrop. Decorative grain, blur, parallax, ambient animation, and unrelated elevation are not used.

## Shapes

Controls use a modest 5px corner; the folder tab and letter-envelope motif carry the physical reference. Round shapes are limited to the postal emblem, status dot, seal, and close button. Source cards use the same restrained corners as the question field. Borders establish hierarchy rather than surrounding every phrase.

## Components

### Foundational visual states

Buttons have explicit hover, pressed, focus-visible, disabled, and busy states. The search button preserves its geometry while busy. Unknown, partial/conflicting, and found results have different text, not color alone. Empty, loading, error, and retry states belong to the same paper surface. A small spinner is the only repeating motion.

### Buttons and actions

The lavender primary action searches the letters. Paper buttons export or retry. Transparent buttons handle source citations and explanations. Every action is a native button; the wordmark and skip link are real anchors. No destructive actions exist. All repeated source-opening behavior uses `openLetter()`.

### Navigation and data display

Ask and Read letters are navigation buttons backed by hash history, with `aria-current`. They are not presented as ARIA tabs. Queries are deliberately excluded from URLs. Letter cards and source cards show meaningful IDs, dates, and authors; arbitrary numbering is avoided. Source citation numbers encode their actual result-list position. Similarity is a numeric model score, never a probability or confidence percentage.

### Forms and overlays

One labeled textarea, an explicit clear button, inline validation, and an explicit-submit flow. The textarea grows with content to 360px and then scrolls. The query persists in memory during navigation or a recoverable request failure. Clear cancels pending work, erases results, and returns focus. Letter and explanation modals use native `dialog.showModal()` for modal semantics and focus containment; close/Escape restore focus to the opener.

### Iconography

Small original line-drawn postal symbols and typographic arrows only. Text accompanies actions. Decorative symbols are hidden from assistive technology. No downloaded assets or icon dependencies.

### Motion

150ms interaction transitions; no entrance choreography. The loading spinner denotes a real local request. Reduced-motion mode disables animations and transitions and uses immediate scrolling.

### Content and data visualization

Voice is quiet and precise. Ask, Search, Read, Clear, and Save are the verbs. The archive and its people are fictional. The UI describes retrieval, not a generative conversation. Missing evidence is an outcome, not a failure to conceal. No charts are needed; similarity is presented as a raw decimal alongside its source.

## Do's and Don'ts

- **Do:** Let readers open every cited source and inspect its surrounding context.
- **Do:** Keep contradictory accounts visible and retain model caveats in exports.
- **Do:** Test the empty, unknown, offline, mobile, keyboard, and reduced-motion states.
- **Don't:** Style similarity as certainty or turn quotation retrieval into testimony.
- **Don't:** Use external fonts, analytics, query persistence, or unrequested network services.
- **Don't:** Add floating ghost characters, animated dust, generic gradients, or fake activity.
