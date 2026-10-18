from provenance.snapshot import take_snapshot, save_snapshot, load_snapshot
from provenance.scanner import scan_plugins
from provenance.differ import diff_snapshot
from tests.conftest import make_plugin
import os
import pytest


def _mutate(pdir, rel, new_content):
    with open(os.path.join(pdir, rel), "w", encoding="utf-8") as f:
        f.write(new_content)


def test_snapshot_captures_state(plugins_dir):
    snap = take_snapshot(plugins_dir)
    assert snap["format_version"] == 1
    assert snap["plugins"]["official-tool"]["version"] == "1.2.0"
    assert snap["plugins"]["sneaky-side"]["mcp_servers"] == ["fs-server", "net-server"]
    assert "hooks/hooks.json" in snap["plugins"]["sneaky-side"]["files"]


def test_snapshot_roundtrip(plugins_dir, tmp_path):
    snap = take_snapshot(plugins_dir)
    path = save_snapshot(snap, os.path.join(str(tmp_path), "snap.json"))
    loaded = load_snapshot(path)
    assert loaded["plugins"] == snap["plugins"]


def test_load_snapshot_rejects_garbage(tmp_path):
    path = os.path.join(str(tmp_path), "bad.json")
    with open(path, "w") as f:
        f.write('{"nope": true}')
    with pytest.raises(ValueError):
        load_snapshot(path)


def test_diff_clean_is_only_sideloaded_advisory(plugins_dir, tmp_path):
    snap = take_snapshot(plugins_dir)
    findings = diff_snapshot(scan_plugins(plugins_dir), snap)
    # nothing drifted; the only finding is the persistent low-severity
    # sideloaded advisory for sneaky-side (scan warnings surface it too)
    assert len(findings) == 1
    assert findings[0]["kind"] == "SIDELOADED_ORIGIN"
    assert findings[0]["severity"] == "low"


def test_diff_flags_version_drift_with_auto_update(plugins_dir, tmp_path):
    snap = take_snapshot(plugins_dir)
    pdir = os.path.join(plugins_dir, "sneaky-side")
    with open(os.path.join(pdir, "plugin.json")) as f:
        import json
        m = json.load(f)
    m["version"] = "0.5.0"
    with open(os.path.join(pdir, "plugin.json"), "w") as f:
        json.dump(m, f)
    findings = diff_snapshot(scan_plugins(plugins_dir), snap)
    drift = [f for f in findings if f["kind"] == "VERSION_DRIFT"]
    assert len(drift) == 1 and drift[0]["severity"] == "high"
    assert "0.4.1 -> 0.5.0" in drift[0]["detail"]
    assert "auto-update ON" in drift[0]["detail"]


def test_diff_flags_new_mcp_server(plugins_dir):
    snap = take_snapshot(plugins_dir)
    pdir = os.path.join(plugins_dir, "official-tool")
    import json
    path = os.path.join(pdir, "plugin.json")
    m = json.load(open(path))
    m["mcp_servers"] = ["docs-server", "ssh-server"]
    json.dump(m, open(path, "w"))
    findings = diff_snapshot(scan_plugins(plugins_dir), snap)
    newmcp = [f for f in findings if f["kind"] == "NEW_MCP_SERVER"]
    assert len(newmcp) == 1 and newmcp[0]["severity"] == "high"
    assert "ssh-server" in newmcp[0]["detail"]


def test_diff_flags_changed_file(plugins_dir):
    snap = take_snapshot(plugins_dir)
    _mutate(os.path.join(plugins_dir, "sneaky-side"), "servers/net.js", "console.log('evil');\n")
    findings = diff_snapshot(scan_plugins(plugins_dir), snap)
    changed = [f for f in findings if f["kind"] == "FILE_CHANGED"]
    assert len(changed) == 1 and changed[0]["severity"] == "high"
    assert "servers/net.js" in changed[0]["detail"]


def test_diff_flags_added_and_removed_files(plugins_dir):
    snap = take_snapshot(plugins_dir)
    pdir = os.path.join(plugins_dir, "official-tool")
    with open(os.path.join(pdir, "newfile.txt"), "w") as f:
        f.write("new")
    os.remove(os.path.join(pdir, "skills/greet/SKILL.md"))
    findings = diff_snapshot(scan_plugins(plugins_dir), snap)
    kinds = {f["kind"] for f in findings}
    assert "FILE_ADDED" in kinds and "FILE_REMOVED" in kinds


def test_diff_flags_plugin_added_and_removed(plugins_dir, tmp_path):
    snap = take_snapshot(plugins_dir)
    make_plugin(plugins_dir, "late-arrival",
                {"name": "late-arrival", "version": "0.1", "source": "local"},
                {"x.txt": "x"})
    import shutil
    shutil.rmtree(os.path.join(plugins_dir, "official-tool"))
    findings = diff_snapshot(scan_plugins(plugins_dir), snap)
    kinds = {f["kind"] for f in findings}
    assert "PLUGIN_ADDED" in kinds and "PLUGIN_REMOVED" in kinds


def test_diff_flags_sideloaded_on_rescan(plugins_dir):
    snap = take_snapshot(plugins_dir)
    findings = diff_snapshot(scan_plugins(plugins_dir), snap)
    side = [f for f in findings if f["kind"] == "SIDELOADED_ORIGIN"]
    assert len(side) == 1 and side[0]["plugin"] == "sneaky-side"
    assert "not independently verified" in side[0]["detail"]


def test_no_mocks_in_tool_code():
    import subprocess, os
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "provenance")
    out = subprocess.run(["grep", "-r", "unittest.mock", root], capture_output=True, text=True)
    assert out.returncode != 0, out.stdout
