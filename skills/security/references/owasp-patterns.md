# OWASP prevention patterns

Prevention patterns, not a ranking. **Python leads** (the primary stack);
TypeScript/Express follows where the shape differs meaningfully.

---

## Injection — SQL, NoSQL, OS command

Never build a query by concatenation. The parameter placeholder is the driver's,
not a format string.

```python
# BAD — string interpolation is injection, in every driver
cur.execute(f"SELECT * FROM users WHERE id = '{user_id}'")

# GOOD — sqlite3 (qmark), values passed separately
cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))

# GOOD — psycopg (pyformat). Note: %s is NOT Python string formatting here.
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# GOOD — SQLAlchemy Core/ORM binds automatically
stmt = select(User).where(User.id == user_id)

# GOOD — raw SQL through SQLAlchemy still binds, via named params
session.execute(text("SELECT * FROM users WHERE id = :uid"), {"uid": user_id})
```

**Identifiers can't be parameterized.** Table and column names must come from an
allowlist, never from user input:

```python
SORTABLE = {"created_at", "name", "priority"}   # allowlist, not validation
if sort_key not in SORTABLE:
    raise ValidationError(f"cannot sort by {sort_key!r}")
cur.execute(f"SELECT * FROM tasks ORDER BY {sort_key}")  # safe: value from allowlist
```

**OS commands** — pass a list, never a shell string:

```python
# BAD: shell=True with any user-derived value
subprocess.run(f"convert {path} out.png", shell=True)

# GOOD: argument list, no shell
subprocess.run(["convert", path, "out.png"], check=True)
```

```ts
// TypeScript
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);
const user2 = await prisma.user.findUnique({ where: { id: userId } });
```

---

## Broken authentication

```python
from argon2 import PasswordHasher          # argon2-cffi; OWASP's first choice
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()                       # sane defaults; don't hand-tune blindly
hashed = ph.hash(plaintext)

try:
    ph.verify(hashed, plaintext)
except VerifyMismatchError:
    ...                                     # wrong password
if ph.check_needs_rehash(hashed):           # params changed since this was stored
    store(ph.hash(plaintext))
```

Compare any other secret in constant time — a plain `==` leaks length and prefix
through timing:

```python
import hmac, secrets
hmac.compare_digest(provided_token, expected_token)
reset_token = secrets.token_urlsafe(32)     # never random.random() for secrets
```

**Session cookies** — all four attributes, every time:

```python
response.set_cookie(
    "session", token,
    httponly=True,      # not readable from JavaScript
    secure=True,        # HTTPS only
    samesite="lax",     # blocks cross-site POST; see the caveat below
    max_age=86400,
)
```

> `samesite="lax"` blocks cross-site *POST* but still permits top-level
> cross-site **GET**. It is not by itself CSRF protection. Keep state-changing
> operations off GET, and use `samesite="strict"` or a CSRF token for
> high-value actions.

```ts
app.use(session({
  secret: process.env.SESSION_SECRET,   // from the environment, never in code
  resave: false, saveUninitialized: false,
  cookie: { httpOnly: true, secure: true, sameSite: 'lax', maxAge: 86_400_000 },
}));
```

---

## Broken access control

**Authentication answers "who are you"; authorization answers "may you."**
Endpoints with the first and not the second are the most common real-world
breach — and no linter catches it.

```python
@app.patch("/api/tasks/{task_id}")
async def update_task(task_id: str, body: TaskUpdate,
                      user: User = Depends(current_user)):
    task = await tasks.get(task_id)
    if task is None or task.owner_id != user.id:
        # 404, not 403 — a 403 confirms the row exists to someone who can't see it
        raise HTTPException(404, "Task not found")
    return await tasks.update(task_id, body)
```

Check ownership on **reads too**, not just writes. `GET /api/tasks/{id}` without
an ownership check is a data leak (IDOR), and it's the endpoint people forget.

---

## Cross-site scripting

```python
# Jinja2: autoescape ON. Never reach for |safe on user data.
# BAD:  {{ user_bio | safe }}
# GOOD: {{ user_bio }}

# If you must accept rich text, sanitize with an allowlist:
import nh3                                   # Rust ammonia bindings; maintained
clean = nh3.clean(user_html)
```

```ts
element.innerHTML = userInput;               // BAD
return <div>{userInput}</div>;               // GOOD — React escapes by default
const clean = DOMPurify.sanitize(userInput); // if raw HTML is truly required
```

Sanitize on **output**, not on input — the same string is safe in JSON, unsafe in
HTML, and unsafe differently inside a `<script>` or a URL attribute.

---

## Input validation at the boundary

Parse into a typed object at the edge; don't validate and then pass the raw dict
along. One function that returns the parsed result or raises — two code paths can
disagree, one can't.

```python
from pydantic import BaseModel, Field
from datetime import datetime

class CreateTask(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    priority: Literal["low", "medium", "high"] = "medium"
    due_date: datetime | None = None
    model_config = {"extra": "forbid"}   # reject unknown keys — mass-assignment guard

@app.post("/api/tasks", status_code=201)
async def create_task(body: CreateTask):     # FastAPI validates; 422 on failure
    return await tasks.create(body)
```

`extra: "forbid"` matters: without it, a client can post `is_admin: true` and
have it silently ride along into a model that happens to accept it.

```ts
const CreateTaskSchema = z.object({
  title: z.string().min(1).max(200).trim(),
  priority: z.enum(['low', 'medium', 'high']).default('medium'),
}).strict();                                  // the Zod equivalent of extra=forbid
const result = CreateTaskSchema.safeParse(req.body);
if (!result.success) return res.status(422).json({ error: result.error.flatten() });
```

---

## File upload safety

**Trust content, not names.** `Content-Type` and the filename are both supplied
by the client and both lie. Check the magic bytes.

```python
# Prefixes are ordered longest-first where they overlap; the first match wins.
MAGIC = (
    (b"\xff\xd8\xff",                 "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n",            "image/png"),
    (b"RIFF",                         "image/webp"),   # plus "WEBP" at offset 8
)
MAX_BYTES = 5 * 1024 * 1024

def sniff(head: bytes) -> str | None:
    """Return the detected content type, or None if it isn't an allowed image."""
    for prefix, mime in MAGIC:
        if head.startswith(prefix):
            if mime == "image/webp" and head[8:12] != b"WEBP":
                return None
            return mime
    return None

def validate_upload(head: bytes, size: int) -> str:
    if size > MAX_BYTES:
        raise ValidationError(f"file too large (max {MAX_BYTES // 1024 // 1024}MB)")
    detected = sniff(head)
    if detected is None:
        raise ValidationError("file type not allowed (jpeg, png, webp only)")
    return detected
```

Also: **never** build the storage path from the client filename
(`../../etc/passwd`) — generate your own name and keep the original only as a
display label. Serve uploads from a separate origin or with
`Content-Disposition: attachment` and `X-Content-Type-Options: nosniff`.

---

## Server-side request forgery

Any time the server fetches a URL the user influenced — webhooks, "import from
URL", image proxies, link previews — an attacker can aim it at internal services.
`169.254.169.254` (cloud metadata) is the number-one target.

Python needs no third-party package for this; `ipaddress` and `socket` are stdlib:

```python
import ipaddress, socket
from urllib.parse import urlparse

ALLOWED_HOSTS = {"hooks.example.com"}

def assert_safe_url(raw: str) -> str:
    url = urlparse(raw)
    if url.scheme != "https":
        raise ValidationError("https only")
    if url.hostname not in ALLOWED_HOSTS:
        raise ValidationError("host not allowed")
    # Resolve ALL records — one private address anywhere fails the check.
    for *_, sockaddr in socket.getaddrinfo(url.hostname, url.port or 443):
        ip = ipaddress.ip_address(sockaddr[0])
        if not ip.is_global:      # covers loopback, link-local, private, ULA, v4+v6
            raise ValidationError(f"resolves to non-public address {ip}")
    return raw
```

`ip.is_global` is the single check that covers loopback, link-local
(`169.254.0.0/16`), private ranges, and IPv6 unique-local.

**Disable redirects** on the fetch (`allow_redirects=False` / `redirect: 'error'`)
— otherwise a public URL can 302 you straight to `127.0.0.1`.

> **TOCTOU caveat.** The HTTP client resolves DNS *again* after your check, so a
> short-TTL record can rebind to an internal IP in between. For high-risk
> surfaces, resolve once and connect to the pinned IP, or put a filtering proxy
> in front. Say so in the code comment rather than implying the check is total.

```ts
// TypeScript equivalent needs a helper for the IP classification
import ipaddr from 'ipaddr.js';
if (addrs.some((a) => ipaddr.parse(a.address).range() !== 'unicast')) throw …;
await fetch(url, { redirect: 'error' });
```

---

## Sensitive data exposure

```python
# Allowlist the fields that go out; never blocklist the ones that don't.
class PublicUser(BaseModel):
    id: str
    display_name: str
    # password_hash, reset_token, email simply have no way to appear here

# Secrets fail closed at startup, not at first use in production
API_KEY = os.environ["STRIPE_API_KEY"]      # KeyError at boot if missing
# not os.environ.get("STRIPE_API_KEY") — that yields None and fails later, quietly
```

A deny-list (`del user["password_hash"]`) breaks the moment someone adds a new
sensitive column. An allowlist model can't.

---

## Security headers and CORS

Python has no `helmet`; set them explicitly in one middleware so there's a single
place to audit.

```python
HEADERS = {
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; "
                               "img-src 'self' data:; connect-src 'self'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
}

@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers.update(HEADERS)
    return response
```

**CORS** — an explicit allowlist, and never `*` together with credentials
(browsers reject the combination, and the intent is wrong anyway):

```python
origins = os.environ["ALLOWED_ORIGINS"].split(",")   # fail closed if unset
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True)
```

Don't default the origin list to a localhost value — a missing env var in
production then silently ships a dev configuration.

---

## Rate limiting

Auth endpoints need a much tighter limit than general traffic; credential
stuffing is the whole reason.

```python
from slowapi import Limiter                  # FastAPI/Starlette
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("10/15minutes")               # vs "100/15minutes" for general API
async def login(...): ...
```

```ts
app.use('/api/',      rateLimit({ windowMs: 15*60_000, max: 100 }));
app.use('/api/auth/', rateLimit({ windowMs: 15*60_000, max: 10 }));
```

Rate-limit by account as well as by IP where you can — a botnet defeats per-IP
limits trivially.

---

## Static sites and frontend bundles

A static site has no server to protect, but the browser is still a boundary:

- **Anything in the client bundle is public.** Build-time variables exposed to
  the client (`PUBLIC_*`, `VITE_*`, `NEXT_PUBLIC_*`) ship to every visitor —
  never put a secret behind those prefixes.
- **Third-party scripts run with your origin's full power.** Prefer
  self-hosting; when loading from a CDN, pin an exact version and add
  `integrity` (SRI) plus `crossorigin="anonymous"`.
- **Set a CSP even for static hosting** (host config or `<meta
  http-equiv="Content-Security-Policy">`), starting from `default-src 'self'`
  and allowlisting only what the page loads.
- **Analytics, fonts, and embeds are data egress.** Each one sends visitor data
  to a third party; it needs a named reason under the privacy principle.

---

## Secrets management

```
.env.example  → committed, placeholder values only
.env          → NOT committed
.env.local    → NOT committed
```

`.gitignore` is a safety device — ignore the class, re-allow only the template:

```gitignore
.env
.env.*
!.env.example
*.pem
*.key
```

Before committing:

```bash
git diff --cached | grep -iE 'password|secret|api_key|token|BEGIN [A-Z ]*PRIVATE KEY'
```

**If a secret ever reaches a remote, rotate it.** Deleting the line or rewriting
history is not enough — assume compromise the moment it's pushed. Revoke and
reissue first, then purge from history.
