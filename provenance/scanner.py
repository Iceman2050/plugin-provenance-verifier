"""Scan a plugins directory (~/.claude/plugins style) and parse each plugin's manifest."""
import hashlib
import json
import os

MANIFEST_NAMES = ("plugin.json", "manifest.json")


def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(plugin_dir):
    """Return (manifest_dict, manifest_path) or raise FileNotFoundError."""
    for name in MANIFEST_NAMES:
        path = os.path.join(plugin_dir, name)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("manifest %s is not a JSON object" % path)
            return data, path
    raise FileNotFoundError("no manifest (plugin.json/manifest.json) in %s" % plugin_dir)


def inventory_files(plugin_dir):
    """Map relative path -> sha256 for every file under plugin_dir, excluding manifests."""
    files = {}
    for root, _dirs, filenames in os.walk(plugin_dir):
        for fn in filenames:
            full = os.path.join(root, fn)
            if fn in MANIFEST_NAMES:
                continue
            rel = os.path.relpath(full, plugin_dir)
            files[rel] = hash_file(full)
    return files


def classify_origin(source_value):
    """Return (origin_label, is_official). Origin is what the manifest *declares*."""
    if not source_value:
        return "undeclared (treated as sideloaded)", False
    v = str(source_value).strip().lower()
    if v in ("official", "anthropic", "claude-plugin-directory", "directory"):
        return "official directory (declared)", True
    if v in ("sideloaded", "local", "third-party", "github", "url", "custom"):
        return "sideloaded (declared)", False
    return "sideloaded (%s, declared)" % source_value, False


def scan_plugins(plugins_dir):
    """Scan each immediate child directory that contains a manifest.

    Returns dict: plugin_id -> record with name, version, origin, auto_update,
    mcp_servers, files (relpath->sha256), and any warnings.
    """
    results = {}
    entries = sorted(os.listdir(plugins_dir)) if os.path.isdir(plugins_dir) else []
    for entry in entries:
        pdir = os.path.join(plugins_dir, entry)
        if not os.path.isdir(pdir):
            continue
        try:
            manifest, manifest_path = load_manifest(pdir)
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
            results[entry] = {"plugin_id": entry, "error": str(exc)}
            continue
        origin_label, is_official = classify_origin(manifest.get("source"))
        record = {
            "plugin_id": entry,
            "name": manifest.get("name", entry),
            "version": str(manifest.get("version", "unknown")),
            "origin": origin_label,
            "official": is_official,
            "origin_note": "declared origin from manifest 'source' field, NOT independently verified",
            "auto_update": bool(manifest.get("auto_update", False)),
            "mcp_servers": sorted(manifest.get("mcp_servers") or manifest.get("bundled_mcp_servers") or []),
            "files": inventory_files(pdir),
            "warnings": [],
        }
        if not is_official:
            record["warnings"].append("SIDELOADED: not from the official plugin directory")
        if record["auto_update"]:
            record["warnings"].append("AUTO-UPDATE ON: bundled code can change silently")
        results[entry] = record
    return results
