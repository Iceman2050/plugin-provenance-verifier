# ACCEPTANCE GATES — plugin-provenance-verifier (built 2026-10-18)

1. GH-NAME: `gh search repos "plugin-provenance-verifier"` returns no exact-name hit. Check: gh search repos command above. DONE 2026-10-18 (only fuzzy matches).
2. PYTEST: `python -m pytest -v` exits 0 with ≥12 tests passing, including ≥8 exercising core logic (scan/snapshot/diff). Check: run in dir, capture output.
3. CLI E2E: `scan` on fixture tree prints plugin inventory incl. declared origin + auto-update + MCP servers; `snapshot` writes snapshot file; after mutating a fixture (new MCP server, changed file, new version with auto-update on), `diff` flags VERSION_DRIFT/AUTO-UPDATE, NEW_MCP_SERVER, FILE_CHANGED. Check: run CLI sequence, grep output.
4. CI: .github/workflows/ci.yml uses checkout@v4, setup-python@v5 (3.12), and `python -m pytest -v` (not bare pytest). Check: grep ci.yml; run the exact CI test command locally.
5. LICENSE: MIT present with "Ingenious AI" attribution line.
6. README: title + 2026-09-25 dated hook with both source links + how-to-run + "## Built by Ingenious AI" + all 11 platform links + "## What it does NOT do".
7. NO MOCKS IN TOOL CODE: grep for unittest.mock in provenance/ == 0 (fixtures in tests only).
8. PUSH: `gh repo create Iceman2050/plugin-provenance-verifier --public --source=<dir> --push --description="<hook>"`; on throttle write PUSH-COMMAND.txt and CONTINUE.
