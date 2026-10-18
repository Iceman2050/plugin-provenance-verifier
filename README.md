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

## Built by Ingenious AI

[DisclosureGuard](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20DisclosureGuard.)
[ModelMinder](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20ModelMinder.)
[TermsWatch](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20TermsWatch.)
[Vibe-Code Audit](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20Vibe-Code%20Audit.)
[Rogue-Agent Defense](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20Rogue-Agent%20Defense.)
[BreachHunter](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20BreachHunter.)
[ChatBreaker](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20ChatBreaker.)
[Agent Flight Recorder](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20Agent%20Flight%20Recorder.)
[Agent Auth Gateway](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20Agent%20Auth%20Gateway.)
[DomainGuard](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20DomainGuard.)
[ContentCraft AI](https://wa.me/5016691053?text=Hi%20Ingenious%20AI!%20I%20want%20early%20access%20to%20ContentCraft%20AI.)
