# Dead Letter Office — UX contract

## Product sources and scope

The project task is the authoritative brief: a new private localhost demo with original fictional letters, local semantic AI retrieval, literal source quotations, citations, and uncertainty. The API contract is implemented by the local Python server (`GET /api/archive`, `POST /api/ask`). No accounts, publishing, payments, personal source uploads, retention settings, deletion, or external side effects are in this interface.

| Business concern | Source | UI consequence |
| --- | --- | --- |
| Permission model | Current project brief: private localhost only | No sharing or publication actions |
| Data lifecycle/privacy | Current project brief: fictional samples; queries local | No browser-storage persistence; query excluded from URL; requests only to same-origin local API |
| Deletion | No mutable archive in current scope | No delete action or misleading edit controls |
| Billing | No paid APIs/accounts in current scope | No purchase, token-credit, or billing UI |
| Truthfulness | Current brief and API result contract | Fiction label, literal quotations, source links, raw similarity rather than confidence, visible limitations |

## Canonical UI map

| Capability | Canonical owner | Source of truth | Allowed variants | Verification |
| --- | --- | --- | --- | --- |
| Form | `web/app.js` question event handlers + `#question-form` | This contract | Explicit-submit inquiry only | Empty validation, retry, clear, edit-during-request |
| Scrollbar | `web/style.css` global baseline | DESIGN.md and CSS tokens | Dialog overflow and textarea overflow | Computed style, narrow viewport, forced colors |
| Dialog | `openDialog()` / `openLetter()` in `web/app.js` | This contract | Read letter / explain model | Keyboard, Escape, source highlighting, focus return |
| Feedback | `announce()` + `#live-status`; inline error and paper states | This contract | Loading / ready / error / unknown / partial / found | Live-region and visual checks |
| Navigation | `navigate()` / `showView()` | This contract | `#ask`, `#letters` | Back/Forward, correct title, selected state |
| Read detail | `openLetter()` | Archive API | Catalogue entry / source passage | Same complete letter; citation opens highlighted passage |

Select/listbox, date picker, table selection, CRUD, and toast overlays are not applicable. Dates are read-only source metadata. The archive is a small bounded sample collection rendered in full, not an unbounded paginated feed.

## Flow ledger

- **Open:** Load archive metadata. Until it arrives, search is disabled. Pure-JavaScript controls start disabled and are enabled only after their handlers are bound; a noscript notice explains the requirement. On error, the paper shows the error and a retry action. Questions never disappear on request failure.
- **Ask:** Explicit form submit or Ctrl/Cmd+Enter. Whitespace-only input receives an associated inline error and field focus. IME composition does not trigger the shortcut. There is no live remote search, therefore no debounce.
- **Pending:** Primary action disabled, stable label geometry, loading announcement. A 20-second timeout ends an unresponsive request. Clear or editing cancels the current request. An incrementing revision prevents stale responses from replacing newer state.
- **Found:** Question, summary, literal quotations, source citations, source cards, and caveat. Scores are similarity values, not truth estimates.
- **Uncertain:** Explicit partial/conflicting-evidence label; quotes and caveat remain visible. Competing accounts must not be collapsed into an invented narrative.
- **Unknown:** Explicit inability to answer; any explanatory limitation remains visible. No fabricated missing quotation.
- **Clear:** Abort request, invalidate old responses, empty field and results, remove validation, focus field. No confirmation is needed for this reversible in-memory inquiry.
- **Read:** Open complete letter from either catalogue or result. Highlight a cited passage when present; no other evidence is hidden. Escape/close restores focus to the original trigger.
- **Navigate:** Hash identifies the view only. Back and Forward restore the prior view. Query and results remain in memory until page reload or clear. No sensitive text enters browser history.
- **Export:** Download a plain-text artifact with fiction label, question, literal quotes, source IDs, full retrieved passages, and limitations. The export is browser-local and initiates only when the user clicks Save.

## Accessibility and resilience

English UI. Semantic headings, buttons, labeled input, live status, visible focus, reduced-motion rules, native modal focus isolation, and natural document scrolling. Target WCAG 2.2 AA; automated checks alone are not a certification. At 320px width, task actions and full letter text must remain reachable. Reader modal height is bounded to the viewport and content scrolls internally. No controls exist only on hover. Source text is inserted with `textContent`, never interpreted as markup.

## Verification boundaries

`node --check web/app.js` verifies syntax, not behavior. Browser testing must exercise actual API integration, empty/unknown/error states, rapid clears and changed queries, source IDs, close/Escape focus, Back/Forward, mobile overflow, reduced motion, and local export. The parent implementation owns model tests and real-server end-to-end evidence. No full accessibility conformance claim is made solely from static review.
