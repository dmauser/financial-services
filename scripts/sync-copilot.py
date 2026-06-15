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
import json
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


UMBRELLA_ROOT = COPILOT / "plugins" / "financial-services"


def _read_frontmatter(md_path: Path) -> dict:
    """Parse a tiny YAML frontmatter (name, description). Returns empty dict on failure."""
    if not md_path.is_file():
        return {}
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    out = {}
    current_key = None
    for line in text[3:end].splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(" ") and current_key:
            out[current_key] += " " + line.strip()
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            current_key = k.strip()
            out[current_key] = v.strip().strip('"').strip("'")
        else:
            current_key = None
    return out


ORCHESTRATOR_HEADER = """---
name: financial-services
description: Umbrella router for the Claude for Financial Services suite. Reads the user's request, identifies which specialist owns the workflow, and dispatches to the right agent or skill. Use as the default entry point when the user asks "what can financial-services do" or describes a task without naming a specialist.
tags: [orchestrator, financial-services]
---

# Financial Services - Orchestrator

You are the Financial Services orchestrator. You don't do the work yourself - you route to one of {n_specialists} specialist agents (or one of {n_commands} slash commands) bundled in this plugin. Mirror the runtime `fs_capabilities` tool from the npx extension: when the user asks "what can you do?", reply with the specialist + slash-command tables below. For any other request, identify the correct specialist (or skill / slash command) and hand off by following its workflow.

## Compliance posture

These workflows draft analyst work product (memos, models, research notes, reconciliations) for human sign-off. Never make investment recommendations, execute transactions, post to ledgers, or approve onboarding autonomously. If the user asks for any of those, decline and explain why.

## Specialists ({n_specialists})

{specialist_table}

## Slash commands ({n_commands})

All slash commands are bundled in this plugin's `commands/` directory and selectable via `/`. Use them as targeted shortcuts when the user names the workflow directly (e.g. "run a DCF on NVDA" -> `/dcf NVDA`).

{command_list}

## Routing rules

1. **Named specialist or slash command** -> hand off directly.
2. **Workflow described, not named** -> match the description against the table above; pick the closest specialist; hand off.
3. **Multi-step / cross-specialist task** -> decompose, hand off to each specialist in sequence; re-orchestrate between handoffs.
4. **Out of scope** (general LLM chat, non-FSI requests) -> answer normally without invoking a specialist.

## Bundled MCP connectors

This plugin ships `.mcp.json` with the same 12 connectors the npx extension installs (factset, daloopa, capiq, lseg, moodys, msft365, box, pitchbook, sec, web, polygon, alpaca). All ship **disabled** - enable individually in the host's `/mcp` UI before invoking workflows that depend on external data.
"""


def _build_specialist_table(specialists: list[tuple[str, str]]) -> str:
    if not specialists:
        return "_(no specialists found)_"
    lines = ["| Specialist | What it does |", "|---|---|"]
    for slug, desc in specialists:
        lines.append(f"| `{slug}` | {desc} |")
    return "\n".join(lines)


def _build_command_list(commands: list[str]) -> str:
    if not commands:
        return "_(no slash commands found)_"
    return "\n".join(f"- `/{c}`" for c in sorted(commands))


def sync_umbrella(dest: Path | None = None) -> int:
    """Synthesize a single umbrella plugin at copilot-cli/plugins/financial-services/
    that bundles all specialist agents, all unique skills, and all slash commands
    in the flat layout the Claude/Copilot plugin loader expects.

    Source of truth: plugins/agent-plugins/, plugins/vertical-plugins/,
    plugins/partner-built/, and copilot-cli/commands/ (already generated from MAPPING.md).

    `dest` overrides the default output path (UMBRELLA_ROOT). Used by check.py to
    regenerate into a temp dir and diff against the committed tree.
    """
    out = dest if dest is not None else UMBRELLA_ROOT
    if out.exists():
        shutil.rmtree(out)
    (out / ".claude-plugin").mkdir(parents=True)
    (out / "agents").mkdir()
    (out / "skills").mkdir()
    (out / "commands").mkdir()

    # Mirror copilot-cli's package version into the plugin manifest.
    pkg_version = "0.0.0"
    pkg = COPILOT / "package.json"
    if pkg.is_file():
        try:
            pkg_version = json.loads(pkg.read_text()).get("version", "0.0.0")
        except json.JSONDecodeError:
            pass

    manifest = {
        "name": "financial-services",
        "version": pkg_version,
        "description": (
            "Umbrella plugin for Claude for Financial Services: 10 specialist agents, "
            "all skills, all 39 slash commands, and an orchestrator that routes between "
            "them. Equivalent to the npx extension delivered as a single Path B install. "
            "Generated by scripts/sync-copilot.py - do not hand-edit."
        ),
        "author": {"name": "dmauser (Copilot CLI port)"},
    }
    (out / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )

    # 1. Specialist agents -> agents/<slug>.md (flat copy)
    specialists: list[tuple[str, str]] = []
    src_root = PLUGINS / "agent-plugins"
    if src_root.is_dir():
        for slug_dir in sorted(p for p in src_root.iterdir() if p.is_dir()):
            slug = slug_dir.name
            src_md = slug_dir / "agents" / f"{slug}.md"
            if not src_md.is_file():
                continue
            shutil.copy2(src_md, out / "agents" / f"{slug}.md")
            fm = _read_frontmatter(src_md)
            specialists.append((slug, fm.get("description", "")))

    # 2. Unique skills, deduped by name across vertical-plugins/, partner-built/,
    #    and any specialist-bundled skills not already covered by a vertical.
    seen_skills: set[str] = set()
    skill_sources: list[Path] = []
    for vp_root in ("vertical-plugins", "partner-built"):
        d = PLUGINS / vp_root
        if not d.is_dir():
            continue
        for vert in sorted(p for p in d.iterdir() if p.is_dir()):
            sk = vert / "skills"
            if not sk.is_dir():
                continue
            for s in sorted(p for p in sk.iterdir() if p.is_dir()):
                if (s / "SKILL.md").is_file():
                    skill_sources.append(s)
    if src_root.is_dir():
        for slug_dir in sorted(p for p in src_root.iterdir() if p.is_dir()):
            sk = slug_dir / "skills"
            if not sk.is_dir():
                continue
            for s in sorted(p for p in sk.iterdir() if p.is_dir()):
                if (s / "SKILL.md").is_file():
                    skill_sources.append(s)
    for s in skill_sources:
        if s.name in seen_skills:
            continue
        seen_skills.add(s.name)
        shutil.copytree(s, out / "skills" / s.name)

    # 3. Slash commands -> commands/<name>.md (flatten copilot-cli/commands/{agents,skills}/<name>/{agent,SKILL}.md)
    command_names: list[str] = []
    cmd_root = COPILOT / "commands"
    for kind, fname in (("agents", "agent.md"), ("skills", "SKILL.md")):
        d = cmd_root / kind
        if not d.is_dir():
            continue
        for entry in sorted(p for p in d.iterdir() if p.is_dir()):
            src_md = entry / fname
            if src_md.is_file():
                shutil.copy2(src_md, out / "commands" / f"{entry.name}.md")
                command_names.append(entry.name)

    # 4. Orchestrator agent (must be last so we have specialist + command lists)
    orchestrator = ORCHESTRATOR_HEADER.format(
        n_specialists=len(specialists),
        n_commands=len(command_names),
        specialist_table=_build_specialist_table(specialists),
        command_list=_build_command_list(command_names),
    )
    (out / "agents" / "financial-services.md").write_text(
        orchestrator, encoding="utf-8"
    )

    # 5. MCP template -> .mcp.json (host /mcp UI reads .mcp.json from plugin root).
    mcp_src = COPILOT / "mcp" / ".mcp.json.template"
    if mcp_src.is_file():
        shutil.copy2(mcp_src, out / ".mcp.json")

    # 6. README
    (out / "README.md").write_text(
        "# financial-services (umbrella plugin)\n\n"
        "Bundles every Claude for Financial Services specialist + skill + slash\n"
        "command into a single Claude/Copilot plugin install. Behaves as a markdown\n"
        "orchestrator (`agents/financial-services.md`) that routes incoming requests\n"
        "to the right specialist.\n\n"
        "**Generated** by `scripts/sync-copilot.py` from the canonical sources under\n"
        "`plugins/agent-plugins/`, `plugins/vertical-plugins/`, `plugins/partner-built/`,\n"
        "and `copilot-cli/commands/`. Do not hand-edit.\n\n"
        "Install:\n\n"
        "```text\n"
        "copilot plugin marketplace add dmauser/financial-services\n"
        "copilot plugin install financial-services@claude-for-financial-services\n"
        "```\n\n"
        "For the runtime tool registration (`fs_capabilities`, `fs_<slug>_role`, ...) use\n"
        "the npx extension instead: `npx -y github:dmauser/financial-services init`.\n",
        encoding="utf-8",
    )

    return len(specialists) + len(seen_skills) + len(command_names) + 1


def sync_copilot_marketplace(dest_dir: Path | None = None) -> int:
    """Write copilot-cli/.copilot-plugin/marketplace.json - a Copilot-dedicated
    marketplace registering only the umbrella `financial-services` plugin.

    Kept separate from the upstream-tracked .claude-plugin/marketplace.json so
    upstream syncs from anthropics/financial-services never conflict on it.
    Users install via local path:

        git clone https://github.com/dmauser/financial-services
        copilot plugin marketplace add ./financial-services/copilot-cli
        copilot plugin install financial-services@financial-services-copilot

    `dest_dir` overrides the output directory (default: copilot-cli/.copilot-plugin/).
    Used by check.py for drift detection.
    """
    out_dir = dest_dir if dest_dir is not None else (COPILOT / ".copilot-plugin")
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "name": "financial-services-copilot",
        "displayName": "Claude for Financial Services (Copilot CLI umbrella)",
        "description": (
            "Copilot-CLI-dedicated marketplace registering the single umbrella plugin "
            "`financial-services`, which bundles all 10 specialist agents, all skills, "
            "all 39 slash commands, and a markdown orchestrator that routes between them. "
            "Source is generated by scripts/sync-copilot.py from the canonical plugins/ tree."
        ),
        "owner": {"name": "dmauser (Copilot CLI port)"},
        "_generated": (
            "GENERATED by scripts/sync-copilot.py - do not edit by hand. "
            "Kept separate from the upstream-tracked .claude-plugin/marketplace.json."
        ),
        "plugins": [
            {
                "name": "financial-services",
                "displayName": "Claude for Financial Services (umbrella)",
                "source": "./plugins/financial-services",
                "description": (
                    "10 specialist agents, all skills, all 39 slash commands, plus a "
                    "markdown orchestrator that routes incoming requests to the right "
                    "specialist - all in a single Claude/Copilot plugin install. "
                    "Functionally equivalent to the npx extension's runtime tools, "
                    "delivered as Path B markdown content."
                ),
            }
        ],
    }
    out = out_dir / "marketplace.json"
    body = json.dumps(payload, indent=2) + "\n"
    if not out.is_file() or out.read_text(encoding="utf-8") != body:
        out.write_text(body, encoding="utf-8")
    return 1


def main() -> int:
    if not COPILOT.is_dir():
        print(f"ERROR: {COPILOT} does not exist - scaffold copilot-cli/ first", file=sys.stderr)
        return 2
    slugs, sf = sync_specialists()
    verticals, vf = sync_verticals()
    cmd_a, cmd_s = sync_commands()
    umbrella = sync_umbrella()
    mkt = sync_copilot_marketplace()
    print(
        f"sync-copilot: {slugs} specialist(s), {verticals} vertical(s), "
        f"{cmd_a} command-agent(s), {cmd_s} command-skill(s), "
        f"{sf + vf} mirrored file(s), {umbrella} umbrella file(s), "
        f"{mkt} copilot marketplace(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
