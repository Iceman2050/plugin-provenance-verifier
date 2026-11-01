# plugin-provenance-verifier

Audit where your Claude Code plugins actually came from — and catch silent drift.

**News hook (2026-09-25):** Anthropic opened the Claude plugin submission portal, and plugin auto-update defaults **ON**. Anthropic itself states it "does not control what MCP servers, files or software are bundled into a plugin" — so the plugin you reviewed at install time is not necessarily the plugin running today. Sources: [Claude Plugins official overview](https://www.agilesingh.com/resources/claude-plugins-official) · [Claude Plugin Directory news](https://reconn-ai.com/news/claude-plugin-directory-ai-visibility/).

This tool scans a plugins directory (e.g. `~/.claude/plugins`), records each plugin's **declared** origin, auto-update setting, bundled MCP servers, and a hash inventory of every bundled file — then diffs later runs against that snapshot to flag anything that changed.

## How to run

```bash
pip install pytest
python -m provenance.cli scan --plugins-dir ~/.claude/plugins
python -m provenance.cli snapshot --plugins-dir ~/.claude/plugins --snapshot-file ~/.claude/plugin-snapshot.json
# ... time passes, plugins update ...
python -m provenance.cli diff --plugins-dir ~/.claude/plugins --snapshot-file ~/.claude/plugin-snapshot.json
```

`diff` flags, with severity:

- `VERSION_DRIFT` (high) — version changed; notes whether auto-update is ON (behavior may have changed silently)
- `NEW_MCP_SERVER` (high) — a bundled MCP server appeared that wasn't there at install time
- `FILE_CHANGED` / `FILE_ADDED` / `FILE_REMOVED` (high/medium) — file drift since the snapshot
- `PLUGIN_ADDED` / `PLUGIN_REMOVED` (medium/high)
- `SIDELOADED_ORIGIN` (low) — declared origin is not the official directory

`scan` also warns on sideloaded plugins and auto-update-ON plugins.

## See it run

Real output, captured 2026-11-01 against a two-plugin demo directory built for
this README (one plugin with auto-update on, one sideloaded from a random URL):

```
== alpha-tool ==
  name:        alpha-tool
  version:     1.0.0
  origin:      sideloaded (official-directory, declared)
  auto_update: True
  mcp_servers: alpha-mcp
  files:       1
  WARNING: SIDELOADED: not from the official plugin directory
  WARNING: AUTO-UPDATE ON: bundled code can change silently
== beta-pack ==
  name:        beta-pack
  version:     0.9.1
  origin:      sideloaded (https://random-site.example/plugins, declared)
  auto_update: False
  mcp_servers: (none)
  files:       1
  WARNING: SIDELOADED: not from the official plugin directory
```

The full suite (25 tests) passes: `python -m pytest -q`.

**Plugins are one surface; your website is the other.** When you want the
site itself checked — exposed files, leaked keys, open doors — the fleet's
free front door is [BreachHunter](https://breachhunter.getingeniousai.com).

## Tests

```bash
python -m pytest -v
```

25 tests, no mocks in the tool code (fixtures live in `tests/`).

## What it does NOT do

- Origin is the **declared** `source` field in the plugin manifest — it is **not** independently verified against the official directory. A malicious manifest can lie; this tool labels what is *claimed*, then catches drift *from that claim*.
- It does not audit what bundled MCP servers *do* at runtime — only that they appeared, changed, or vanished.
- It does not block updates or uninstall plugins; it is a read-only audit, not a guardrail.
- If a plugin rewrites its own manifest to hide a change, only the file-hash inventory (which ignores manifests) and version-diff logic catch it.

---

## Built by Ingenious AI

- [DisclosureGuard](https://disclosureguard.getingeniousai.com) — AI disclosure compliance
- [ModelMinder](https://modelminder.getingeniousai.com) — model deprecation radar
- [TermsWatch](https://termswatch.getingeniousai.com) — AI vendor terms watcher
- [Vibe-Code Audit](https://vibe-audit.getingeniousai.com) — vibe-coded app security audit
- [Rogue-Agent Defense](https://rogue-defense.getingeniousai.com) — rogue agent protection
- [BreachHunter](https://breachhunter.getingeniousai.com) — breach detection
- [ChatBreaker](https://chatbreaker.getingeniousai.com) — chatbot jailbreak testing
- [Agent Flight Recorder](https://flightrecorder.getingeniousai.com) — hash-chained agent logging
- [Agent Auth Gateway](https://authgateway.getingeniousai.com) — agent budget caps & kill switch
- [DomainGuard](https://domainguard.getingeniousai.com) — domain-impersonation defense
- [ContentCraft AI](https://contentcraft.getingeniousai.com) — AI content studio

All 11 platforms, one suite deal: [Security Suite](https://ingeniousai-security-checks-mirror-0e97b6.gitlab.io/security-suite.html)
