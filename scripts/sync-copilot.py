#!/usr/bin/env python3
"""Mirror plugins/ canonical sources into copilot-cli/.

Single source of truth stays in plugins/vertical-plugins/ (skills, commands)
and plugins/agent-plugins/ (system prompts). This script propagates byte-for-byte
copies into copilot-cli/, where the Copilot CLI extension/plugin loads them.

Mapping:
  plugins/agent-plugins/<slug>/agents/<slug>.md
    -> copilot-cli/extensions/financial-services/specialists/<slug>/agents/<slug>.md
  plugins/agent-plugins/<slug>/skills/<name>/
    -> copilot-cli/extensions/financial-services/specialists/<slug>/skills/<name>/
  plugins/vertical-plugins/<vertical>/skills/<name>/
    -> copilot-cli/verticals/<vertical>/skills/<name>/
  plugins/vertical-plugins/<vertical>/commands/<cmd>.md
    -> copilot-cli/verticals/<vertical>/commands/<cmd>.md
  plugins/vertical-plugins/<vertical>/.mcp.json
    -> copilot-cli/verticals/<vertical>/.mcp.json   (informational only)
  plugins/partner-built/<slug>/...
    -> copilot-cli/verticals/<slug>/...

Idempotent. Run after editing anything under plugins/.
"""
from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
COPILOT = ROOT / "copilot-cli"

SPECIALIST_ROOT = COPILOT / "extensions" / "financial-services" / "specialists"
VERTICAL_ROOT = COPILOT / "verticals"
COMMANDS_ROOT = COPILOT / "commands"
MAPPING = COPILOT / "commands" / "MAPPING.md"


def copy_tree(src: Path, dst: Path) -> int:
    """Copy src -> dst, overwriting; return number of files copied."""
    if not src.exists():
        return 0
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return sum(1 for _ in dst.rglob("*") if _.is_file())


def copy_file(src: Path, dst: Path) -> bool:
    if not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_file() and filecmp.cmp(src, dst, shallow=False):
        return False
    shutil.copy2(src, dst)
    return True


def sync_specialists() -> tuple[int, int]:
    files = 0
    slugs = 0
    SPECIALIST_ROOT.mkdir(parents=True, exist_ok=True)
    src_root = PLUGINS / "agent-plugins"
    if not src_root.is_dir():
        return 0, 0
    for src_slug in sorted(p for p in src_root.iterdir() if p.is_dir()):
        slug = src_slug.name
        slugs += 1
        # System prompt
        agent_md = src_slug / "agents" / f"{slug}.md"
        dst_md = SPECIALIST_ROOT / slug / "agents" / f"{slug}.md"
        if copy_file(agent_md, dst_md):
            files += 1
        # Bundled skills
        src_skills = src_slug / "skills"
        dst_skills = SPECIALIST_ROOT / slug / "skills"
        if src_skills.is_dir():
            if dst_skills.exists():
                shutil.rmtree(dst_skills)
            shutil.copytree(src_skills, dst_skills)
            files += sum(1 for _ in dst_skills.rglob("*") if _.is_file())
    return slugs, files


def sync_verticals() -> tuple[int, int]:
    verticals = 0
    files = 0
    VERTICAL_ROOT.mkdir(parents=True, exist_ok=True)

    sources = []
    vp = PLUGINS / "vertical-plugins"
    if vp.is_dir():
        sources.extend(sorted(p for p in vp.iterdir() if p.is_dir()))
    pb = PLUGINS / "partner-built"
    if pb.is_dir():
        sources.extend(sorted(p for p in pb.iterdir() if p.is_dir()))

    for src in sources:
        verticals += 1
        dst = VERTICAL_ROOT / src.name
        # skills/
        for sub in ("skills", "commands"):
            s = src / sub
            d = dst / sub
            if s.is_dir():
                if d.exists():
                    shutil.rmtree(d)
                shutil.copytree(s, d)
                files += sum(1 for _ in d.rglob("*") if _.is_file())
        # informational mcp config
        for f in (".mcp.json",):
            if (src / f).is_file():
                if copy_file(src / f, dst / f):
                    files += 1
    return verticals, files


def parse_mapping() -> list[tuple[str, str, str, str]]:
    """Return list of (command, vertical, kind, source_path) from MAPPING.md."""
    if not MAPPING.is_file():
        return []
    rows = []
    in_table = False
    import re as _re
    for line in MAPPING.read_text(encoding="utf-8").splitlines():
        if line.startswith("|---"):
            in_table = True
            continue
        if not in_table or not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) != 4:
            continue
        cmd, vertical, kind, src = cells
        cmd = cmd.strip("`/")
        m = _re.match(r"`([^`]+)`", src)
        src_path = m.group(1) if m else src
        if kind in ("agent", "skill"):
            rows.append((cmd, vertical, kind, src_path))
    return rows


WRAPPER_AGENT = """---
name: {cmd}
description: {description}
source: {source}
tags: [command-agent, {vertical}]
---

# /{cmd}

Wrapper for the `/{cmd}` slash command (vertical: **{vertical}**, kind: **agent**).

The full workflow lives in [`{source}`]({source}). When this agent is selected,
load that file's instructions verbatim and execute its workflow. Inputs and
clarification questions are defined there.

This wrapper is **generated** by `scripts/sync-copilot.py` from
`commands/MAPPING.md`. Do not hand-edit.
"""

WRAPPER_SKILL = """---
name: {cmd}
description: {description}
source: {source}
trigger: |
  User explicitly invokes /{cmd}, or asks for the workflow described in {source}.
tags: [command-skill, {vertical}]
---

# /{cmd}

Skill wrapper for the `/{cmd}` slash command (vertical: **{vertical}**).

The full instructions live in [`{source}`]({source}). On invocation, follow that
file's workflow exactly.

This wrapper is **generated** by `scripts/sync-copilot.py` from
`commands/MAPPING.md`. Do not hand-edit.
"""


def extract_description(src_md: Path) -> str:
    if not src_md.is_file():
        return f"(source missing: {src_md})"
    text = src_md.read_text(encoding="utf-8", errors="replace")
    if text.startswith("---"):
        try:
            _, fm, _ = text.split("---", 2)
            for line in fm.splitlines():
                if line.startswith("description:"):
                    return line.split(":", 1)[1].strip().strip('"').strip("'")
        except ValueError:
            pass
    for line in text.splitlines():
        if line.strip() and not line.startswith("#"):
            return line.strip()[:160]
    return ""


def sync_commands() -> tuple[int, int]:
    rows = parse_mapping()
    if not rows:
        return 0, 0
    # Wipe and regenerate to keep the tree exactly in step with MAPPING.md.
    for sub in ("agents", "skills"):
        d = COMMANDS_ROOT / sub
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)

    agents = skills = 0
    for cmd, vertical, kind, src in rows:
        src_path = COPILOT / src
        description = extract_description(src_path)
        if kind == "agent":
            d = COMMANDS_ROOT / "agents" / cmd
            d.mkdir(parents=True, exist_ok=True)
            (d / "agent.md").write_text(
                WRAPPER_AGENT.format(cmd=cmd, vertical=vertical, source=src, description=description),
                encoding="utf-8",
            )
            agents += 1
        elif kind == "skill":
            d = COMMANDS_ROOT / "skills" / cmd
            d.mkdir(parents=True, exist_ok=True)
            (d / "SKILL.md").write_text(
                WRAPPER_SKILL.format(cmd=cmd, vertical=vertical, source=src, description=description),
                encoding="utf-8",
            )
            skills += 1
    return agents, skills


def main() -> int:
    if not COPILOT.is_dir():
        print(f"ERROR: {COPILOT} does not exist - scaffold copilot-cli/ first", file=sys.stderr)
        return 2
    slugs, sf = sync_specialists()
    verticals, vf = sync_verticals()
    cmd_a, cmd_s = sync_commands()
    print(
        f"sync-copilot: {slugs} specialist(s), {verticals} vertical(s), "
        f"{cmd_a} command-agent(s), {cmd_s} command-skill(s), "
        f"{sf + vf} mirrored file(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
