#!/usr/bin/env python3
"""
Lint all plugin + managed-agent manifests and verify cross-file references.

Checks:
  1. Every *.yaml under managed-agents/ parses.
  2. Every plugin.json / marketplace.json / steering-examples.json parses.
  3. Every <vertical>/agents/*.md has valid YAML frontmatter with name + description.
  4. Every system.file, skills[].path, callable_agents[].manifest in agent.yaml
     and subagent yamls resolves to an existing file/dir.
  5. Every managed-agents/<slug>/ has agent.yaml, README.md, steering-examples.json.

Exit 0 if clean, 1 otherwise. Requires: pyyaml.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
MANAGED = ROOT / "managed-agent-cookbooks"
errors: list[str] = []
checked = 0


def ensure_hooks_installed() -> None:
    """Point git at .githooks so the version-bump pre-commit runs.

    Native equivalent of Husky's `prepare`, piggybacked on the script
    everyone already runs before committing. Best-effort: never fatal.
    """
    want = ".githooks"
    try:
        cur = subprocess.run(
            ["git", "-C", str(ROOT), "config", "--get", "core.hooksPath"],
            capture_output=True, text=True,
        ).stdout.strip()
        if cur != want:
            subprocess.run(
                ["git", "-C", str(ROOT), "config", "core.hooksPath", want],
                check=True, capture_output=True,
            )
            print(f"[check.py] installed git hooks (core.hooksPath -> {want})")
    except (subprocess.SubprocessError, OSError):
        pass  # not a git checkout / git unavailable — ignore


# Install hooks before anything that can exit early (e.g. missing pyyaml),
# so a fresh checkout still gets the version-bump hook wired up.
ensure_hooks_installed()

try:
    import yaml
except ImportError:
    print("ERROR: requires pyyaml (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)


def err(msg: str) -> None:
    errors.append(msg)


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


# --- 1. YAML parse ----------------------------------------------------------
for yml in sorted(MANAGED.rglob("*.yaml")):
    checked += 1
    try:
        with open(yml) as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        err(f"YAML parse: {rel(yml)}: {e}")

# --- 2. JSON parse ----------------------------------------------------------
json_globs = [
    ".claude-plugin/marketplace.json",
    "plugins/**/.claude-plugin/plugin.json",
    "managed-agent-cookbooks/*/steering-examples.json",
]
for pat in json_globs:
    for jf in sorted(ROOT.glob(pat)):
        checked += 1
        try:
            json.loads(jf.read_text())
        except json.JSONDecodeError as e:
            err(f"JSON parse: {rel(jf)}: {e}")

# --- 3. agent.md frontmatter -----------------------------------------------
for md in sorted(PLUGINS.glob("agent-plugins/*/agents/*.md")):
    checked += 1
    text = md.read_text()
    if not text.startswith("---"):
        err(f"frontmatter: {rel(md)}: missing leading ---")
        continue
    try:
        _, fm, _ = text.split("---", 2)
        meta = yaml.safe_load(fm)
        for k in ("name", "description"):
            if k not in meta:
                err(f"frontmatter: {rel(md)}: missing '{k}'")
    except (ValueError, yaml.YAMLError) as e:
        err(f"frontmatter: {rel(md)}: {e}")


# --- 4. reference resolution -----------------------------------------------
def check_refs(yml: Path) -> None:
    try:
        data = yaml.safe_load(yml.read_text()) or {}
    except yaml.YAMLError:
        return  # already reported above
    base = yml.parent

    sys_spec = data.get("system")
    if isinstance(sys_spec, dict) and "file" in sys_spec:
        p = (base / sys_spec["file"]).resolve()
        if not p.is_file():
            err(f"ref: {rel(yml)}: system.file -> {sys_spec['file']} (not found)")

    for s in data.get("skills") or []:
        if isinstance(s, dict) and "path" in s:
            p = (base / s["path"]).resolve()
            if not p.exists():
                err(f"ref: {rel(yml)}: skills.path -> {s['path']} (not found)")
        if isinstance(s, dict) and "from_plugin" in s:
            p = (base / s["from_plugin"]).resolve()
            if not (p / "skills").is_dir():
                err(f"ref: {rel(yml)}: skills.from_plugin -> {s['from_plugin']} (no skills/ dir)")

    for c in data.get("callable_agents") or []:
        if isinstance(c, dict) and "manifest" in c:
            p = (base / c["manifest"]).resolve()
            if not p.is_file():
                err(f"ref: {rel(yml)}: callable_agents.manifest -> {c['manifest']} (not found)")


for yml in sorted(MANAGED.rglob("*.yaml")):
    check_refs(yml)

# --- 4b. agent-plugin bundled skills match vertical source -----------------
import filecmp  # noqa: E402
import re  # noqa: E402

src_by_name = {p.name: p for p in PLUGINS.glob("vertical-plugins/*/skills/*") if p.is_dir()}
for bundled in sorted(PLUGINS.glob("agent-plugins/*/skills/*")):
    if not bundled.is_dir():
        continue
    src = src_by_name.get(bundled.name)
    if not src:
        err(f"bundled-skill: {rel(bundled)}: no vertical-plugins source named '{bundled.name}'")
        continue
    cmp = filecmp.dircmp(src, bundled)
    if cmp.diff_files or cmp.left_only or cmp.right_only:
        err(
            f"bundled-skill: {rel(bundled)}: drifted from {rel(src)} "
            f"(run scripts/sync-agent-skills.py)"
        )

# --- 4b2. agent.md skill references exist in the agent's own bundle --------
for md in sorted(PLUGINS.glob("agent-plugins/*/agents/*.md")):
    slug = md.parents[1].name
    sk_dir = PLUGINS / "agent-plugins" / slug / "skills"
    bundle = {p.name for p in sk_dir.iterdir() if p.is_dir()} if sk_dir.is_dir() else set()
    for ref in set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", md.read_text())):
        if ref in src_by_name and ref not in bundle:
            err(
                f"agent-prose: {rel(md)}: references `{ref}` but "
                f"plugins/agent-plugins/{slug}/skills/{ref}/ is not bundled"
            )

# --- 4d. copilot-cli/ mirror is in sync with plugins/ source ---------------
COPILOT = ROOT / "copilot-cli"
if COPILOT.is_dir():
    spec_root = COPILOT / "extensions" / "financial-services" / "specialists"
    # 4d.1 each specialist's agent.md and bundled skills/ match agent-plugins/<slug>/
    for src_slug in sorted((PLUGINS / "agent-plugins").iterdir()):
        if not src_slug.is_dir():
            continue
        slug = src_slug.name
        src_md = src_slug / "agents" / f"{slug}.md"
        dst_md = spec_root / slug / "agents" / f"{slug}.md"
        if src_md.is_file():
            if not dst_md.is_file():
                err(f"copilot-mirror: missing {rel(dst_md)} (run scripts/sync-copilot.py)")
            elif src_md.read_bytes() != dst_md.read_bytes():
                err(f"copilot-mirror: {rel(dst_md)} drifted from {rel(src_md)} "
                    f"(run scripts/sync-copilot.py)")
        src_sk = src_slug / "skills"
        dst_sk = spec_root / slug / "skills"
        if src_sk.is_dir():
            if not dst_sk.is_dir():
                err(f"copilot-mirror: missing {rel(dst_sk)}/ (run scripts/sync-copilot.py)")
            else:
                cmp = filecmp.dircmp(src_sk, dst_sk)
                # recurse manually to catch deep drift
                def _walk(c):
                    if c.diff_files or c.left_only or c.right_only:
                        return True
                    return any(_walk(sub) for sub in c.subdirs.values())
                if _walk(cmp):
                    err(f"copilot-mirror: {rel(dst_sk)}/ drifted from {rel(src_sk)}/ "
                        f"(run scripts/sync-copilot.py)")
    # 4d.2 each vertical's skills/ and commands/ match its plugins/vertical-plugins/ source
    vert_root = COPILOT / "verticals"
    src_verticals = []
    for vp_root, _ in (("vertical-plugins", None), ("partner-built", None)):
        d = PLUGINS / vp_root
        if d.is_dir():
            src_verticals.extend(p for p in d.iterdir() if p.is_dir())
    for src in sorted(src_verticals):
        for sub in ("skills", "commands"):
            s = src / sub
            d = vert_root / src.name / sub
            if not s.is_dir():
                continue
            if not d.is_dir():
                err(f"copilot-mirror: missing {rel(d)}/ (run scripts/sync-copilot.py)")
                continue
            cmp = filecmp.dircmp(s, d)
            def _walk(c):
                if c.diff_files or c.left_only or c.right_only:
                    return True
                return any(_walk(sub) for sub in c.subdirs.values())
            if _walk(cmp):
                err(f"copilot-mirror: {rel(d)}/ drifted from {rel(s)}/ "
                    f"(run scripts/sync-copilot.py)")
    # 4d.3 copilot-cli/package.json parses
    pkg = COPILOT / "package.json"
    if pkg.is_file():
        checked += 1
        try:
            json.loads(pkg.read_text())
        except json.JSONDecodeError as e:
            err(f"JSON parse: {rel(pkg)}: {e}")
    # 4d.4 mcp template parses
    mcp_t = COPILOT / "mcp" / ".mcp.json.template"
    if mcp_t.is_file():
        checked += 1
        try:
            json.loads(mcp_t.read_text())
        except json.JSONDecodeError as e:
            err(f"JSON parse: {rel(mcp_t)}: {e}")
    # 4d.5 umbrella plugin tree + .copilot-plugin/marketplace.json are
    # in lock-step with what scripts/sync-copilot.py would generate from
    # the canonical sources. Re-run the generator into a temp tree and
    # diff so any hand-edit (or out-of-date sync) shows up as drift.
    umbrella = COPILOT / "plugins" / "financial-services"
    cp_mp = COPILOT / ".copilot-plugin" / "marketplace.json"
    if umbrella.is_dir() or cp_mp.is_file():
        import importlib.util as _ilu
        import tempfile as _tmp
        spec = _ilu.spec_from_file_location(
            "_sync_copilot", ROOT / "scripts" / "sync-copilot.py"
        )
        sc = _ilu.module_from_spec(spec)
        try:
            spec.loader.exec_module(sc)
        except Exception as e:
            err(f"copilot-mirror: failed to import sync-copilot.py for drift check: {e}")
        else:
            with _tmp.TemporaryDirectory() as td:
                tmp_root = Path(td)
                shadow_umbrella = tmp_root / "umbrella"
                shadow_mp_dir = tmp_root / "mp"
                try:
                    sc.sync_umbrella(dest=shadow_umbrella)
                    sc.sync_copilot_marketplace(dest_dir=shadow_mp_dir)
                except Exception as e:
                    err(f"copilot-mirror: drift-check generator raised: {e}")
                else:
                    if umbrella.is_dir() and shadow_umbrella.is_dir():
                        cmp = filecmp.dircmp(umbrella, shadow_umbrella)
                        def _walk_u(c):
                            if c.diff_files or c.left_only or c.right_only:
                                return True
                            return any(_walk_u(sub) for sub in c.subdirs.values())
                        if _walk_u(cmp):
                            err(f"copilot-mirror: {rel(umbrella)}/ drifted from "
                                f"sync-copilot.py output (run scripts/sync-copilot.py)")
                        checked += 1
                    shadow_mp_file = shadow_mp_dir / "marketplace.json"
                    if cp_mp.is_file() and shadow_mp_file.is_file():
                        if cp_mp.read_text(encoding="utf-8") != shadow_mp_file.read_text(encoding="utf-8"):
                            err(f"copilot-mirror: {rel(cp_mp)} drifted from "
                                f"sync-copilot.py output (run scripts/sync-copilot.py)")
                        checked += 1

# --- 4c. marketplace source paths resolve ----------------------------------
mp = ROOT / ".claude-plugin" / "marketplace.json"
for p in json.loads(mp.read_text()).get("plugins", []):
    src = (ROOT / p["source"]).resolve()
    if not (src / ".claude-plugin" / "plugin.json").is_file():
        err(f"marketplace: {p['name']} source -> {p['source']} (no plugin.json)")

# --- 5. required files per managed-agent -----------------------------------
for d in sorted(MANAGED.iterdir()):
    if not d.is_dir():
        continue
    for req in ("agent.yaml", "README.md", "steering-examples.json"):
        if not (d / req).is_file():
            err(f"missing: {rel(d)}/{req}")

# --- report ----------------------------------------------------------------
if errors:
    print(f"FAIL — {len(errors)} issue(s) across {checked} file(s):\n", file=sys.stderr)
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    sys.exit(1)
print(f"OK — {checked} file(s) checked, 0 issues.")
