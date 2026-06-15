# Financial Services Plugins

Cowork plugins and Claude Managed Agent templates for financial services. Each named agent ships two ways from one source.

## Repository Structure

```
├── plugins/
│   ├── agent-plugins/               #   named agents — one self-contained plugin each
│   │   └── <slug>/
│   │       ├── .claude-plugin/plugin.json
│   │       ├── agents/<slug>.md     #   ← canonical system prompt (one source, three wrappers)
│   │       └── skills/              #   ← bundled copies, synced from vertical-plugins/
│   ├── vertical-plugins/            #   FSI verticals — skill sources, commands, MCPs
│   │   └── <vertical>/
│   │       ├── .claude-plugin/plugin.json
│   │       ├── commands/
│   │       ├── skills/
│   │       └── .mcp.json
│   └── partner-built/               #   partner plugins (LSEG, S&P Global)
├── managed-agent-cookbooks/         # CMA cookbooks (one dir per named agent)
│   └── <slug>/
│       ├── agent.yaml               #   system + skills → ../../plugins/agent-plugins/<slug>/...
│       ├── subagents/*.yaml         #   depth-1 leaf workers
│       ├── steering-examples.json
│       └── README.md                #   security tier + handoff notes
├── copilot-cli/                     # GitHub Copilot CLI port (third delivery channel)
│   ├── package.json                 #   semver; same per-branch single-bump policy as plugin.json
│   ├── bin/cli.mjs                  #   `npx financial-services` installer (init / status / mcp enable …)
│   ├── extension.mjs · registry.mjs #   Copilot CLI SDK entrypoints
│   ├── extensions/financial-services/specialists/<slug>/  ← mirror of plugins/agent-plugins/<slug>/
│   ├── verticals/<vertical>/        #   ← mirror of plugins/vertical-plugins/<vertical>/
│   ├── commands/                    #   /comps, /dcf, … wrappers (12 agents + 27 skills) generated from MAPPING.md
│   ├── mcp/.mcp.json.template       #   12 connectors, disabled by default
│   └── instructions/                #   AGENTS.md + path-specific .instructions.md
├── claude-for-msft-365-install/     # admin tooling for the Microsoft 365 add-in (separate from FSI plugins)
└── scripts/                         # deploy-managed-agent.sh, check.py, validate.py, orchestrate.py, sync-agent-skills.py, sync-copilot.py
```

Run `python3 scripts/check.py` before committing — it lints every manifest, verifies all `system.file` / `skills.path` / `callable_agents.manifest` references resolve, and fails if any `agent-plugins/<slug>/skills/` copy has drifted from its `vertical-plugins/` source **or** any file under `copilot-cli/` has drifted from its `plugins/` source. **Edit skills in `vertical-plugins/`**, then run `python3 scripts/sync-agent-skills.py` (propagates into agent bundles) and `python3 scripts/sync-copilot.py` (propagates into `copilot-cli/`).

`check.py` also self-installs a `pre-commit` hook (`git config core.hooksPath .githooks` — no Husky/Node). The hook patch-bumps any plugin's `.claude-plugin/plugin.json` `version` so a branch ends up exactly one patch ahead of `main` (bumped once, not per commit — a plugin's `version` gates update delivery to already-installed users). The `version-bump` GitHub Action enforces the same rule on PRs as a backstop. Bypass a single commit with `git commit --no-verify`; bump logic lives in `scripts/version_bump.py`.

## Key Files

- `marketplace.json`: Marketplace manifest - registers all plugins with source paths
- `plugin.json`: Plugin metadata - name, description, version, and component discovery settings
- `commands/*.md`: Slash commands invoked as `/plugin:command-name`
- `skills/*/SKILL.md`: Detailed knowledge and workflows for specific tasks
- `*.local.md`: User-specific configuration (gitignored)
- `mcp-categories.json`: Canonical MCP category definitions shared across plugins

## Development Workflow

1. Edit markdown files directly - changes take effect immediately
2. Test commands with `/plugin:command-name` syntax
3. Skills are invoked automatically when their trigger conditions match
