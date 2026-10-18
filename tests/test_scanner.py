from provenance.scanner import scan_plugins, load_manifest, classify_origin
import os
import json
import pytest


def test_scan_parses_official_plugin(plugins_dir):
    rec = scan_plugins(plugins_dir)["official-tool"]
    assert rec["name"] == "official-tool"
    assert rec["version"] == "1.2.0"
    assert rec["official"] is True
    assert rec["mcp_servers"] == ["docs-server"]
    assert "skills/greet/SKILL.md" in rec["files"]
    assert rec["warnings"] == []


def test_scan_flags_sideloaded_origin(plugins_dir):
    rec = scan_plugins(plugins_dir)["sneaky-side"]
    assert rec["official"] is False
    assert any("SIDELOADED" in w for w in rec["warnings"])
    assert "declared" in rec["origin"] and "independently verified" in rec["origin_note"]


def test_scan_flags_auto_update_on(plugins_dir):
    rec = scan_plugins(plugins_dir)["sneaky-side"]
    assert rec["auto_update"] is True
    assert any("AUTO-UPDATE" in w for w in rec["warnings"])
    assert scan_plugins(plugins_dir)["official-tool"]["auto_update"] is False


def test_scan_records_bundled_mcp_servers(plugins_dir):
    rec = scan_plugins(plugins_dir)["sneaky-side"]
    assert rec["mcp_servers"] == ["fs-server", "net-server"]


def test_scan_reports_missing_manifest(tmp_path):
    os.makedirs(os.path.join(str(tmp_path), "broken-plugin"))
    rec = scan_plugins(str(tmp_path))["broken-plugin"]
    assert "error" in rec
    assert "no manifest" in rec["error"]


def test_scan_reports_malformed_manifest(tmp_path):
    pdir = os.path.join(str(tmp_path), "bad-json")
    os.makedirs(pdir)
    with open(os.path.join(pdir, "plugin.json"), "w") as f:
        f.write("{not valid json")
    rec = scan_plugins(str(tmp_path))["bad-json"]
    assert "error" in rec


def test_scan_skips_non_directory_files(tmp_path):
    with open(os.path.join(str(tmp_path), "README.md"), "w") as f:
        f.write("hello")
    assert scan_plugins(str(tmp_path)) == {}


def test_scan_empty_dir_is_empty(tmp_path):
    assert scan_plugins(str(tmp_path)) == {}


def test_classify_origin_variants():
    assert classify_origin("official")[1] is True
    assert classify_origin("Anthropic")[1] is True
    assert classify_origin("github")[1] is False
    assert classify_origin("")[1] is False
    assert classify_origin(None)[1] is False


def test_manifest_alternate_name(tmp_path):
    pdir = os.path.join(str(tmp_path), "alt")
    os.makedirs(pdir)
    with open(os.path.join(pdir, "manifest.json"), "w") as f:
        json.dump({"name": "alt", "version": "2.0", "source": "sideloaded"}, f)
    manifest, path = load_manifest(pdir)
    assert manifest["name"] == "alt"
    assert path.endswith("manifest.json")


def test_load_manifest_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_manifest(str(tmp_path))


def test_inventory_hashes_match_file_content(plugins_dir):
    from provenance.scanner import hash_file
    import hashlib
    p = os.path.join(plugins_dir, "official-tool", "skills/greet/SKILL.md")
    expected = hashlib.sha256(open(p, "rb").read()).hexdigest()
    rec = scan_plugins(plugins_dir)["official-tool"]
    assert rec["files"]["skills/greet/SKILL.md"] == expected
