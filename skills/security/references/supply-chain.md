# Supply-chain hygiene

Audits find **known advisories**. They do not prove a package is trustworthy, or
that vulnerable code is reachable, or that an unreviewed install script is safe
to execute. Those are three different questions.

---

## Find the installation boundary first

Don't assume npm, and don't treat the nearest manifest as the install root.

1. **Locate the workspace root that owns the lockfile.** A nested project counts
   as independent only when it sits *outside* that workspace.
2. **Corroborate the manager** from `packageManager` (when present), the lockfile
   on disk, and what CI actually runs. **Stop on disagreement** — competing
   lockfiles at one boundary (`package-lock.json` beside `pnpm-lock.yaml`) mean
   nobody knows what ships.
3. **Pin the manager version** so local and CI resolve identically.

| Ecosystem | Lockfile | Reproducible install | Audit |
|---|---|---|---|
| uv | `uv.lock` | `uv sync --frozen` | `uv export --no-hashes > req.txt && uvx pip-audit -r req.txt` |
| pip | `requirements.txt` w/ hashes | `pip install --require-hashes -r …` | `pip-audit` |
| npm | `package-lock.json` | `npm ci` | `npm audit` |
| pnpm | `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` | `pnpm audit` |
| yarn | `yarn.lock` | `yarn install --immutable` | `yarn npm audit` |

CI must use the frozen/immutable form. An install that can silently resolve a
different version than the lockfile isn't reproducible, and a non-reproducible
install can't be audited meaningfully.

---

## Block install-time code execution

Installing a package runs code **before** you've read a line of it. Block it,
inspect, then approve the minimum.

**Node** — npm and pnpm run `preinstall`/`install`/`postinstall` scripts:

```bash
npm ci --ignore-scripts          # bootstrap with scripts off
# inspect the pending scripts, then allow only what genuinely needs them
```

pnpm ≥10 blocks scripts by default and requires explicit
`onlyBuiltDependencies` entries — keep that policy committed.

**Python** — the analogue is source distributions: a `sdist` executes its build
backend (`setup.py`, PEP 517 hooks) at install time. Wheels do not.

```bash
uv sync --frozen --no-build       # wheels only; nothing executes at install
pip install --only-binary=:all: -r requirements.txt
```

When a package genuinely has no wheel, that's the moment to read its build
script — not to shrug and allow all builds.

**Never blanket-approve scripts.** Commit the policy so the decision is
reviewable, then verify with a clean frozen install from scratch.

---

## Triaging audit results

```
Audit reports a vulnerability
├── critical / high
│   ├── Is the vulnerable code reachable — runtime, build, test, or deploy path?
│   │   ├── YES → fix now (update, patch, or replace)
│   │   └── NO  (confirmed unused across all four) → fix soon, not a blocker
│   └── Is a fix available?
│       ├── YES → update to the patched version
│       └── NO  → workaround, replace the dependency, or allowlist with a review date
├── moderate
│   ├── reachable in production → fix next release cycle
│   └── dev-only               → backlog
└── low
    └── fix during regular dependency updates
```

The questions that decide it:

- Is the vulnerable **function** actually called on any of your paths?
- Runtime dependency or dev-only?
- Exploitable in *your* deployment context — a server-side RCE in a package you
  only use in a build step is a different risk than the same CVE in your API?

**When you defer, write down why and set a review date.** An undocumented
deferral is indistinguishable from an oversight six months later.

---

## Never auto-apply forced remediation

```bash
npm audit fix --force      # ← don't
```

Forced fixes cross declared dependency ranges and can land major-version bumps
with breaking changes, in a commit that looks like routine security maintenance.
Preview the remediation, read the changelogs, and test each resulting upgrade.

---

## Reviewing a new dependency

Audits catch known advisories; they do **not** catch a package that is newly
malicious or typosquatted. Review the dependency, the lockfile diff, and any
script-policy change **together**:

- **Ownership** — who publishes it, and did that change recently?
- **Maintenance** — commit recency, open critical issues, bus factor
- **Release age** — a version published hours ago, pulled in automatically, is
  the classic compromise window
- **Provenance** — verify signatures where supported (`npm audit signatures`,
  `pnpm audit signatures`). Absence is a signal to investigate, not proof of
  compromise
- **Transitive graph** — what does it drag in? A 40-dependency tree for a
  string-padding function is the risk, not the function
- **Typosquats** — `cross-env` vs `crossenv`, `python-dateutil` vs `dateutil`.
  Read the name character by character when adding it

Maps to OWASP A06 (vulnerable and outdated components) and LLM03 (supply chain).

Every dependency needs a stated justification anyway — what it
does and why the standard library can't. That rule is itself a supply-chain
control: the dependency you didn't add can't be compromised.

---

## Checklist

- [ ] One authoritative lockfile per installation boundary, committed
- [ ] CI uses that manager's frozen/immutable install
- [ ] Install scripts blocked unless explicitly approved, policy committed
- [ ] Native audit triaged by reachability and fix risk, not by count
- [ ] No forced auto-remediation
- [ ] New dependencies reviewed: ownership, provenance, release age, transitive
      graph, typosquat check
