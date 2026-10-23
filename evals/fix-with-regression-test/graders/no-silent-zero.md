---
type: llm
---

PASS if, for an empty list, the fixed function does NOT silently return 0 — it returns None, raises a clear error, or the response explicitly flags returning 0 as a choice the user should confirm.
FAIL if it silently returns 0 (or 0.0) for an empty list without flagging that 0 is indistinguishable from a real average of zero.
