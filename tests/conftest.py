"""Fixture builders for plugin-provenance-verifier tests."""
import json
import os
import pytest


def make_plugin(base, pid, manifest, files=None):
    pdir = os.path.join(str(base), pid)
    os.makedirs(pdir, exist_ok=True)
    with open(os.path.join(pdir, "plugin.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f)
    for rel, content in (files or {}).items():
        full = os.path.join(pdir, rel)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
    return pdir


@pytest.fixture
def plugins_dir(tmp_path):
    make_plugin(tmp_path, "official-tool", {
        "name": "official-tool", "version": "1.2.0", "source": "official",
        "auto_update": False, "mcp_servers": ["docs-server"]},
        {"skills/greet/SKILL.md": "# greet\nSay hi.\n"})
    make_plugin(tmp_path, "sneaky-side", {
        "name": "sneaky-side", "version": "0.4.1", "source": "github",
        "auto_update": True, "mcp_servers": ["fs-server", "net-server"]},
        {"hooks/hooks.json": "{}", "servers/net.js": "console.log('x');\n"})
    return str(tmp_path)


@pytest.fixture
def single_official(tmp_path):
    make_plugin(tmp_path, "official-tool", {
        "name": "official-tool", "version": "1.0.0", "source": "official",
        "auto_update": False, "mcp_servers": []},
        {"SKILL.md": "# skill\n"})
    return str(tmp_path)
