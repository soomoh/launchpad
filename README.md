# Launchpad

Launchpad turns Claude Code into a careful development partner. Install it
once, and Claude plans before it builds, writes tests with its code, checks
security and design as it goes, and stops secrets from being committed —
without you having to ask each time.

## What changes when you use it

- **New project or big feature?** Claude writes a short plan first and asks
  you about the decisions that matter, with a recommendation for each.
- **Writing or fixing code?** It follows solid engineering habits, and a bug
  fix comes with a test that proves it.
- **Anything touching logins, uploads, payments, or personal data?** It
  applies security checks before writing the code.
- **Building a page or app screen?** It sets up a consistent look, checks
  accessibility, and avoids the generic "AI-made" style.
- **Finished a piece of work?** It reviews what changed before calling it done.
- **Committing?** A guard stops Claude from committing passwords, keys, or
  your personal details.

## Install

You need [Claude Code](https://claude.com/claude-code) and Python 3.10 or
newer (check with `python3 --version`). Works on macOS, Linux, and Windows
through WSL; plain Windows without WSL isn't supported.

In Claude Code, run:

```
/plugin install launchpad --marketplace soomoh/launchpad
```

If that command isn't recognised, update Claude Code (`claude update`) and try
again.

## Get started

1. Run the setup once:

   ```
   /launchpad:setup
   ```

   It checks your existing Claude Code setup for anything that clashes with
   Launchpad and offers a few recommended safety settings. It asks before
   changing anything.

2. Work as you normally would. Launchpad steps in at the right moments on its
   own. Try something like:

   > I want to build a small app for my book club to track what we're reading.

You can also call any part directly, for example `/launchpad:project-plan`,
`/launchpad:design`, or `/launchpad:quality-audit`. Type `/launchpad:` to see
them all.

## Optional extras

- **Stronger secret checks:** install [gitleaks](https://github.com/gitleaks/gitleaks).
  Launchpad's guard uses it automatically when it's there.
- **Block your own personal details:** list your name, email, or address, one
  per line, in `~/.claude/privacy-terms.local`. The guard will refuse commits
  that contain them. Once you've run setup, Claude can't read this file.

## Already have your own setup?

Your own instructions always come first. If your `CLAUDE.md` or settings
disagree with Launchpad, Claude follows yours. Running `/launchpad:setup`
shows you where they clash, so you can decide.

## Turn it off or remove it

- **Pause the automatic guidance** but keep the tools: open `/config` and
  switch off *Load Launchpad's workflow guidance each session*.
- **Remove it completely:** `/plugin uninstall launchpad`.

## Is it safe?

Launchpad's own code runs only on your computer: it sends nothing anywhere
and collects no data. Its scripts are tested, and its behaviour is measured
against plain Claude Code — [see the results](docs/evals/RESULTS.md).

## Credits and license

Parts of the security and design guidance were inspired by
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) and
[Trystan-SA/claude-design-system-prompt](https://github.com/Trystan-SA/claude-design-system-prompt);
see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

MIT licensed — see [LICENSE](LICENSE). Want to contribute? See
[CONTRIBUTING.md](CONTRIBUTING.md).
