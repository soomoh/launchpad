---
name: engineering
description: Standards for writing, debugging, testing, and reviewing code — root-cause debugging protocol, code design vocabulary (data over code, parse don't validate, guard clauses, normalize at the boundary, error containment), testing standards (fixtures over mocks, pin the catastrophic failure mode, regression test per bug), dependency rules, and style. Use whenever code is being written, changed, debugged, tested, or reviewed, and when judging a codebase's maintainability.
---

# Engineering standards

The project's own conventions win where they exist; these fill the gaps and
set the bar for review.

## Process rules

1. **No new dependency, service, or build step without justification** — what
   it does and why the standard library or what already exists can't. Every
   dependency is attack surface; every service or build step is one more
   thing to run, upgrade, and fix.
2. **Tests ship with code.** Not strict TDD, but nothing lands untested. State
   what each test pins down. A bug fix includes the regression test that
   would have caught it, seen failing before the fix and passing after when
   you can run tests — and when you can't (no shell, code shown in a reply),
   still write them and show them with the fix.
3. **Subtract before adding.** Before adding a feature, option, or setting the
   user didn't ask for, ask what breaks without it. When new code replaces
   old, delete the old path in the same change. No commented-out code; a TODO
   states the condition under which it gets done, or it is deleted.
4. **Protect what others depend on.** Once anyone but the author may hold
   data or habits built on it (a release, a shared tool, a deployed site),
   the stable surface — saved data and file formats, schema, CLI flags,
   config keys, URLs — changes only with a migration that is safe to run
   twice, a backup step in the upgrade notes, and a test that loads
   old-format data. Before that, say in the change summary what changed.
5. **Verify environment assumptions before using them.** Check the actual
   interpreter or runtime version before using recent syntax. Code written for
   Python 3.12 crashes on a system `python3` that is 3.10. When environment and
   intent disagree, flag it — don't silently downgrade.
6. **Run what you wrote.** Executing the real program on realistic input
   catches what unit tests and type checkers miss.
7. **Multi-line edits use the Edit tool.** A scripted edit asserts exactly
   one match per replacement, and never slices between two index lookups
   without asserting their order.

## Debugging: root cause, not symptoms

1. Reproduce it.
2. Explain **why** it breaks — the mechanism, not just the location.
3. Fix it at the level where the cause lives.
4. Add a test that would have caught it.
5. Check whether the same cause has siblings elsewhere.

Two failure patterns recur — look for them:

- **One case's fix is another case's bug.** Splitting dates on whitespace
  fixes one input format's time suffix and silently destroys another format's
  space-containing dates. After fixing for input A, re-verify B and C.
- **"Skip" and "stop" are different decisions.** When scanning messy input,
  "invalid" can mean ignorable noise, end of data, or a genuine error.
  Enumerate them explicitly instead of handling all three the same way.

## Code design vocabulary

Apply these, and name them in code and review when you do:

- **Never hand-roll a solved problem.** `line.split(",")` is not a CSV parser;
  string concatenation is not SQL parameterization; regex is not an HTML
  parser. If the standard library has a module for it, use it.
- **Data over code.** Behavior that varies by case belongs in a table walked
  by unchanging logic — adding a case means adding a line, not a branch.
- **Strategy pattern via first-class functions** over a growing if/elif chain.
- **Parse, don't validate.** One function returns the parsed result or
  `None`/raises — two code paths can disagree; one can't.
- **Sentinels are not zero.** `None` ("no value") differs from `0`/`""` ("an
  empty value"). Never conflate them to save an `if`.
- **Guard clauses.** Handle failures early; keep the happy path unindented.
- **Normalize at the boundary.** Clean external input once, on ingestion.
- **Trust content, not names.** Filenames, extensions, and labels lie; derive
  truth from the data (magic bytes, actual fields) when it matters.
- **Graceful degradation with actionable messages.** A user's mistake
  degrades the run; only a programmer's mistake may crash. Every error message
  says what was expected and what to do next.
- **Error containment scope.** `try/except` wraps one unit of work. Broad
  catches only at such boundaries, with the error surfaced; bare `except:`
  never.
- **EAFP over LBYL** in Python.
- **Duplication is cheaper than the wrong abstraction** — extract on the
  second or third occurrence, not in anticipation.

## Testing standards

- The project's runner; otherwise **pytest** (Python) or **Vitest** (JS/TS).
  Plain functions with `assert`.
- **Fixture files over mocks** for parsing and IO: small, **synthetic**,
  realistic samples committed to the repo — fabricated data, real layout.
- **Pin the catastrophic failure mode explicitly** (money: sign errors; auth:
  false allow; privacy: data egress) with assertions that target it directly.
- **Test the seam, not the surface.** Logic in importable functions; `main()`,
  CLIs, and route handlers stay thin.
- Parametrize same-shape cases; built-in fixtures (`tmp_path`) over manual
  setup and teardown.
- **Code that reads user-supplied input gets a malformed-input table** —
  empty, truncated, wrong encoding, oversized, boundary values. Each one
  degrades with a message; none crashes.
- **Real-browser checks use Playwright** — setup, sandbox-safe running, and
  CI per `${CLAUDE_PLUGIN_ROOT}/skills/engineering/references/browser-testing.md`.

## Style

- **A rule a tool can check belongs to the tool.** When a review finding
  recurs, add a lint rule or test rather than a note.
- **Model instructions you write are code** (skills, agents, CLAUDE.md,
  prompts). First they do the job reliably and repeatably; then every line
  earns its context. One rule lives in one place.
- Type hints on signatures; in Python, `X | None` over `Optional[X]`,
  `pathlib.Path` over `os.path`, f-strings, and a `NamedTuple` or `dataclass`
  once a record has 3+ fields or crosses a function boundary.
- Docstrings state what the function returns and any non-obvious contract
  (units, sign conventions, sentinel meanings).
- Comments explain **why**, never what — terse, for a stranger reading cold.
  For keyword lists, lookaround regexes, and ordering-sensitive logic, comment
  the reason for the order.
- Database access: parameterized queries, always.
