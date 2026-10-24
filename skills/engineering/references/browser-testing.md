# Browser testing with Playwright

The default when a project needs its UI exercised in a real browser:
interaction flows, file inputs, keyboard and focus, anything a unit test can't
see. The machine already has Playwright's Chromium and its system libraries
(the personal install script pins the version); a project only adds the npm
package and a config.

## Set up (once per project)

1. **Pin the package to the machine's browser version** —
   `npm i -D @playwright/test@<version>` where `<version>` is the
   `PLAYWRIGHT_VERSION` in the user's install script (check it; don't guess).
   The same version reuses the shared browser in `~/.cache/ms-playwright`, so
   nothing downloads. A different version needs
   `npx playwright install chromium` (network: Playwright's CDN), so prefer
   matching.
2. **Config** — `playwright.config.ts`:

   ```ts
   import { defineConfig, devices } from '@playwright/test';

   export default defineConfig({
     testDir: 'tests/e2e',
     testMatch: '**/*.spec.ts', // unit tests stay *.test.ts for Vitest
     use: { baseURL: 'http://localhost:4173' },
     projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
     // Playwright starts the app itself, so server and browser share one
     // process tree (and one sandbox decision) — see "Sandbox" below.
     webServer: {
       command: 'npm run dev -- --port 4173 --strictPort',
       url: 'http://localhost:4173',
       reuseExistingServer: !process.env.CI,
     },
   });
   ```

3. **Script** — `"test:e2e": "playwright test"` in `package.json`, and add
   `test-results/` and `playwright-report/` to `.gitignore`.
4. **CI** — mirror the local command: a step
   `npx playwright install --with-deps chromium`, then `npm run test:e2e`.

## Running it

Run through `npm run test:e2e` (or `npx playwright test`), never by starting
a dev server in one command and a browser in another. Chromium needs local
sockets the Bash sandbox blocks, and two sandboxed commands don't share
`localhost`; the user's settings exclude exactly these two commands from the
sandbox. If they still fail with `socket() failed: Operation not permitted`,
the exclusion is missing — tell the user rather than bypassing the sandbox
ad hoc.

**Only in repos the user wrote.** The exclusion runs the repo's test code
outside the sandbox without asking. In a cloned or third-party repo, read its
tests and Playwright config first and ask the user before running them.

## Rules

- **Fixtures only.** Tests drive the app with the project's synthetic fixture
  files — never real user data, never files from gitignored inboxes.
- **No network beyond localhost.** For local-first apps, assert it: route every
  non-localhost request to a failure and expect none.
- **Test behaviour, not pixels.** Prefer role- and label-based locators
  (`getByRole`, `getByLabel`) — they double as an accessibility check.
- Keep the suite small and fast: a smoke path per main flow, not a mirror of
  the unit tests.
