---
name: security
description: Gateway for security-sensitive work — carries the non-negotiable boundary rules (what to always do, what needs human approval, what never to do), the red flags, and routes to threat modelling, OWASP prevention patterns, supply-chain hygiene, and LLM/AI security. Invoke when building anything that accepts user input, implements auth, stores or transmits sensitive data, integrates external APIs, adds file uploads or webhooks, handles payments or PII, calls an LLM, or when the user asks to harden, audit, or security-review code.
---

# Security — boundary rules and routing

Treat every external input as hostile, every secret as sacred, and every
authorization check as mandatory. **Security isn't a phase** — it's a constraint
on every line that touches user data, authentication, or external systems.

Concrete patterns live in `references/`; this file is the judgment and the
routing. Read the reference you need, not all three.

## Threat-model before you harden

Controls bolted on without a threat model are guesses. **If you can't name the
trust boundaries for a feature, you're not ready to secure it** — that's OWASP
A04 Insecure Design, and most breaches begin in design, not code.

For anything non-trivial, run the `launchpad:threat-model` skill first. For a small change
on an already-modelled surface, the short version is enough: where does untrusted
data cross in, what's worth stealing, and how would you misuse this feature?

## The three-tier boundary system

### Always — no exceptions

- Validate all external input **at the system boundary** (route handlers, form
  handlers, message consumers), not deep in the call stack
- Parameterize every database query — never build SQL by concatenation
- Encode output to prevent XSS; use the framework's auto-escaping and don't
  bypass it
- HTTPS for all external communication
- Hash passwords with argon2 / scrypt / bcrypt — never plaintext, never a bare
  hash function
- Set security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)
- Session cookies are `httpOnly`, `secure`, and `sameSite`
- Run the detected package manager's native audit against the committed lockfile
  before every release

### Ask first — needs human approval

- New authentication flows, or changes to auth logic
- Storing a new category of sensitive data (PII, payment info, health data)
- New external service integrations
- CORS configuration changes
- New file upload handlers
- Changes to rate limiting or throttling
- Granting elevated permissions or roles

These are decisions with blast radius. Propose, explain the trade-off, wait.

### Never

- Never commit secrets to version control
- Never log sensitive data (passwords, tokens, full card numbers, session IDs)
- Never treat client-side validation as a security boundary
- Never disable a security header for convenience
- Never pass user-controlled data to `eval`, `exec`, `innerHTML`, a shell, or a
  file path without validation
- Never store auth tokens in client-accessible storage (`localStorage`)
- Never expose stack traces or internal error detail to users

## Red flags — stop and fix

- User input reaching a database query, shell command, or HTML render directly
- Secrets in source or in commit history
- Endpoints with authentication but **no authorization** — the most common real
  breach, and the one linters never catch
- Missing CORS config, or a wildcard `*` origin
- No rate limiting on authentication endpoints
- Stack traces or internal errors surfaced to users
- Competing lockfiles at one installation boundary, non-reproducible installs, or
  blanket-approved dependency scripts
- The server fetching a user-supplied URL without an allowlist (SSRF)
- LLM output flowing into a query, the DOM, a shell, or `eval`
- Secrets, PII, or the full system prompt placed inside an LLM context window

## Rationalizations to reject

| Rationalization | Reality |
|---|---|
| "It's an internal tool" | Internal tools get compromised. Attackers target the weakest link. |
| "We'll add security later" | Retrofitting is far harder than building it in. Add it now. |
| "No one would exploit this" | Automated scanners will find it. Obscurity is not security. |
| "The framework handles it" | Frameworks provide tools, not guarantees. You still have to use them correctly. |
| "It's just a prototype" | Prototypes become production. |
| "Threat modelling is overkill here" | Five minutes of "how would I attack this?" prevents design flaws no control can patch later. |
| "It's just LLM output, it's only text" | That text can be a SQL statement, a script tag, or a shell command. |
| "The audit passed, so the dependency is safe" | Audits match *known* advisories. They don't detect a newly malicious package or make unreviewed install scripts safe to run. |

## Route

| Situation | Where to go |
|---|---|
| Designing a feature; boundaries not yet named | `launchpad:threat-model` skill |
| Writing or reviewing code: injection, authn/authz, XSS, SSRF, validation, uploads, secrets, headers, rate limits | `references/owasp-patterns.md` |
| Dependencies, lockfiles, audits, install scripts, typosquats | `references/supply-chain.md` |
| The app calls an LLM — chatbot, summarizer, agent, RAG | `references/llm-security.md` |
| Reviewing pending changes on a branch | built-in `security-review` |
| Whole-codebase audit before sharing or publishing | `launchpad:quality-audit` (includes git history) |
| Recording the threat model for a project | link its table from `.claude/PLAN.md` (`launchpad:project-plan`) |

## Verification

After implementing security-relevant code, confirm each of these — and **run the
checks rather than asserting them**:

- Native audit has no unmitigated, reachable critical/high findings; CI preserves
  the authoritative lockfile and blocks unreviewed dependency scripts
- No secrets in source or git history — `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/commit_guard.py" --history .`
  (the same scanner blocks Claude's commits via the PreToolUse hook)
- All external input validated at system boundaries
- **Authorization** — not just authentication — checked on every protected
  endpoint, including the ones that only read
- Security headers present in the actual response (check the wire, not the code)
- Error responses don't expose internals
- Rate limiting active on auth endpoints
- Server-side URL fetches validated against an allowlist
- LLM output validated and encoded before use, if AI features are present

A regression test accompanies every security fix — the test that would have
caught it. For security work the catastrophic failure mode to pin explicitly is
**false allow**: assert that an unauthorized request is *refused*, not merely
that an authorized one succeeds.
