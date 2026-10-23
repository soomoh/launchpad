---
name: threat-model
description: Map trust boundaries, name the assets worth protecting, run STRIDE over each boundary, and write abuse cases beside the use cases — before writing security controls. Use at design time when starting a feature that touches user input, auth, money, PII, or external systems; when the user asks "how would this be attacked", "threat model this", or "what could go wrong"; and when project-plan finds a non-trivial trust boundary.
---

# Threat Model

Controls bolted on without a threat model are guesses. **Five minutes of "how
would I attack this?" prevents the design flaws no control can patch later** —
this is OWASP A04 Insecure Design, and most breaches begin in design, not code.

This is a design-time activity. For reviewing code that already exists, use the
`launchpad:security` gateway and its references; for reviewing pending changes on a branch,
use `/security-review`.

## Phase 1: Map the trust boundaries

**Where does untrusted data cross into the system?** Enumerate concretely — a
boundary you don't name is a boundary you don't defend:

- HTTP requests: path params, query strings, bodies, headers, cookies
- Form fields and file uploads
- Webhooks and third-party callbacks
- Responses from external APIs (yes — a compromised or hostile upstream is
  untrusted input)
- Message queues, cron payloads, imported files
- **LLM output**, if the system calls a model
- Anything read from disk that a user could have influenced

For each: what's on the untrusted side, what's on the trusted side, and what
crosses. Draw it if the system has more than three or four.

If you cannot name the trust boundaries for a feature, **you are not ready to
secure it** — stop and map them.

## Phase 2: Name the assets

What is actually worth stealing or breaking? Be specific — "user data" is not an
asset, "the password reset token table" is.

Typical: credentials and session tokens, PII, payment data, admin actions, money
movement, the ability to send mail from your domain, compute (crypto mining),
and reputation (defacement, spam).

Rank them. The control budget follows the asset value, not the feature's
prominence.

## Phase 3: Run STRIDE over each boundary

A quick lens, not a ceremony. For each boundary × each threat, ask the question;
most cells are "not applicable" and that's fine — the value is in the ones that
aren't.

| Threat | Ask | Typical mitigation |
|---|---|---|
| **S**poofing | Can someone impersonate a user or service? | Authentication, signature verification on webhooks |
| **T**ampering | Can data be altered in transit or at rest? | HTTPS, integrity checks, parameterized queries |
| **R**epudiation | Can an action be denied later? | Audit logging of security events |
| **I**nformation disclosure | Can data leak? | Encryption, field allowlists, generic error messages |
| **D**enial of service | Can it be overwhelmed? | Rate limiting, input size caps, timeouts |
| **E**levation of privilege | Can a user gain rights they shouldn't? | Authorization checks, least privilege |

Two that get missed most often, so ask them explicitly:

- **Elevation via missing authorization on reads.** `GET /thing/{id}` with
  authentication but no ownership check is the classic IDOR.
- **Information disclosure via error messages.** A 403 where a 404 belongs
  confirms a record exists to someone who shouldn't know.

## Phase 4: Write abuse cases beside the use cases

For each feature, write the misuse next to the intended use — **and make the
abuse case your first test.**

```
Use case:   A user uploads a profile photo.
Abuse case: A user uploads a PHP file renamed .jpg and requests it back.
            → test: upload with a mismatched magic byte is rejected
Abuse case: A user uploads a 4GB file.
            → test: request exceeding the size cap is rejected before buffering
Abuse case: A user sets the filename to ../../etc/passwd.
            → test: stored path is generated, never derived from client input
```

The catastrophic failure mode for security is **false allow**. Assert that the
unauthorized request is *refused* — a test that only proves the happy path
succeeds would pass on a system with authorization entirely removed.

## Phase 5: Record it

Produce a short, scannable table — this is a working document, not a compliance
artifact:

| Boundary | Asset at risk | Threat (STRIDE) | Mitigation | Where it lives |
|---|---|---|---|---|
| `POST /api/upload` | Server compute, other users | Tampering, DoS | Magic-byte sniff, 5MB cap, generated path | `uploads.py:validate_upload` |

Close with:

- **Accepted risks** — what you're deliberately not defending, and why. An
  undocumented accepted risk is indistinguishable from an oversight later.
- **Open questions** — what needs a decision before build.

Save the table as `.claude/THREAT_MODEL.md` (gitignored with the other
`.claude/*.md` artifacts) and link it from `.claude/PLAN.md` rather than
restating it there.

Then implement against `launchpad:security` and its `references/owasp-patterns.md`.
