import json
import os
import subprocess
import sys

CLI = [sys.executable, "-m", "provenance.cli"]


def test_cli_scan_end_to_end(plugins_dir, capsys):
    from provenance.cli import main
    rc = main(["scan", "--plugins-dir", plugins_dir])
    out = capsys.readouterr().out
    assert rc == 0
    assert "official-tool" in out and "sneaky-side" in out
    assert "declared" in out  # declared-origin labeling
    assert "AUTO-UPDATE" in out


def test_cli_snapshot_then_diff_detects_drift(single_official, tmp_path, capsys):
    from provenance.cli import main
    snapfile = os.path.join(str(tmp_path), "snap.json")
    assert main(["snapshot", "--plugins-dir", single_official, "--snapshot-file", snapfile]) == 0
    assert os.path.isfile(snapfile)
    capsys.readouterr()
    assert main(["diff", "--plugins-dir", single_official, "--snapshot-file", snapfile]) == 0
    assert "no drift" in capsys.readouterr().out

    # mutate: bump version w/ auto-update on, add MCP server, change a file
    pdir = os.path.join(single_official, "official-tool")
    mpath = os.path.join(pdir, "plugin.json")
    m = json.load(open(mpath))
    m.update({"version": "1.1.0", "auto_update": True, "mcp_servers": ["shell-server"]})
    json.dump(m, open(mpath, "w"))
    with open(os.path.join(pdir, "SKILL.md"), "w") as f:
        f.write("# skill changed\n")
    rc = main(["diff", "--plugins-dir", single_official, "--snapshot-file", snapfile])
    out = capsys.readouterr().out
    assert rc == 1  # high-severity findings -> exit 1
    assert "VERSION_DRIFT" in out
    assert "NEW_MCP_SERVER" in out
    assert "FILE_CHANGED" in out
