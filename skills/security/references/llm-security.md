# Securing AI / LLM features

If the app calls an LLM — chatbot, summarizer, agent, RAG — it inherits a new
attack surface. Mapped to the OWASP Top 10 for LLM Applications (2025).

The single most useful reframe: **the model is not a trust boundary.** It is a
text transformer that untrusted input can steer. Everything it emits is
untrusted input to whatever consumes it next.

---

## LLM05 — Improper output handling

**Treat all model output as untrusted input.** Never pass it straight into
`eval`, SQL, a shell, `innerHTML`, or a file path. Validate and encode it exactly
as you would a raw HTTP body.

```python
# BAD — the model's output becomes a command
sql = await llm.generate(f"Write SQL for: {question}")
await db.execute(sql)                       # arbitrary query execution

# BAD — stored XSS, delivered via the model
container.innerHTML = await llm.reply(message)
```

```python
# GOOD — output is data: parse defensively, validate, then act through an allowlist
class Command(BaseModel):
    action: Literal["search", "summarize", "export"]
    params: dict[str, str]
    model_config = {"extra": "forbid"}

try:
    intent = Command.model_validate_json(await llm.reply_json(message))
except (ValidationError, json.JSONDecodeError):
    raise ValidationError("unexpected model output")

await run_allowlisted_action(intent.action, intent.params)
```

Note what makes this safe: the model chooses *among* actions you already
implemented. It never supplies the action itself.

---

## LLM01 — Prompt injection

**Assume prompts can be hijacked.** Any untrusted text in the context window — a
user message, a fetched web page, a PDF, a code comment, a filename — can carry
instructions the model will follow.

**The system prompt is not a security boundary.** "Never reveal X" and "only
answer questions about Y" are steering, not enforcement. Anything the model must
not do has to be impossible in code:

- Enforce permissions at the tool/API layer, checked against the *user's*
  identity — never against what the model asserts
- Don't give the model a tool whose misuse you couldn't tolerate
- Treat retrieved documents as data to be quoted, not instructions to be obeyed;
  keep them clearly delimited from your instructions

Indirect injection is the harder case: the attacker never talks to your app, they
just leave instructions on a page your agent will read.

---

## LLM02 / LLM07 — Sensitive information disclosure

**Keep secrets and other users' data out of prompts.** Anything in the context
can be echoed back — by a crafted request, or by accident.

- No API keys, credentials, or internal endpoints in prompts
- No cross-tenant data in a shared context window
- Don't paste the full system prompt where the model can repeat it
- Redact PII before it reaches the provider unless you've decided, explicitly,
  that it may leave the boundary

Privacy comes first: sending user data to an LLM provider **is** an
external transmission. It needs a named reason, not a default.

---

## LLM06 — Excessive agency

Scope tools to the minimum that does the job:

- Narrow the tool surface — a `read_file` restricted to one directory beats a
  general filesystem tool
- **Require confirmation for destructive or irreversible actions** — deletes,
  payments, emails, anything outward-facing
- Validate every tool argument as untrusted input, because it is: the model
  produced it, possibly under attacker influence
- Prefer read-only tools; make write tools explicit and few

---

## LLM10 — Unbounded consumption

Cap tokens, request rate, and loop/recursion depth so a crafted input can't run
up cost or hang the system:

```python
MAX_TOKENS, MAX_STEPS = 4096, 10
for step in range(MAX_STEPS):            # bounded, not `while True`
    ...
else:
    raise AgentError("step budget exhausted")   # fail loudly, don't spin
```

Rate-limit per account, not just per IP, and put a hard ceiling on spend.

---

## LLM08 — Vector and embedding weaknesses

In RAG, the vector store is a **trust boundary**:

- **Partition embeddings per tenant** and filter by tenant at query time, not
  after retrieval — one user must not be able to retrieve another's documents
- **Validate documents before indexing.** Poisoned content sits in the store and
  steers answers long after ingestion; it's a persistent injection vector
- Treat retrieved chunks as quoted evidence, not as instructions

---

## Checklist

- [ ] Model output never reaches `eval`, SQL, a shell, `innerHTML`, or a path
- [ ] Output parsed into a validated schema before use; allowlisted actions only
- [ ] Permissions enforced in code against the user's identity, not in the prompt
- [ ] Secrets, cross-tenant data, and the system prompt kept out of the context
- [ ] Tools scoped to minimum; destructive actions require confirmation
- [ ] Tool arguments validated as untrusted input
- [ ] Token, rate, and loop-depth caps in place
- [ ] RAG: embeddings partitioned per tenant, filtered at query time; documents
      validated before indexing
