# financial-services (umbrella plugin)

Bundles every Claude for Financial Services specialist + skill + slash
command into a single Claude/Copilot plugin install. Behaves as a markdown
orchestrator (`agents/financial-services.md`) that routes incoming requests
to the right specialist.

**Generated** by `scripts/sync-copilot.py` from the canonical sources under
`plugins/agent-plugins/`, `plugins/vertical-plugins/`, `plugins/partner-built/`,
and `copilot-cli/commands/`. Do not hand-edit.

Install:

```text
copilot plugin marketplace add dmauser/financial-services
copilot plugin install financial-services@financial-services-copilot
```

## MCP connectors (opt-in)

`.mcp.json` ships **empty** - Copilot CLI's plugin host attempts to connect
to every server listed there on plugin load (it ignores `disabled: true`),
and most upstream connectors require paid subscriptions. To enable one:

1. Open `.mcp.json.template` (sibling file) for the catalog of 12 connectors.
2. Copy the entry you want into `.mcp.json`'s `mcpServers` object.
3. Supply credentials per the provider docs.
4. Restart Copilot CLI.

For the runtime tool registration (`fs_capabilities`, `fs_<slug>_role`, ...) use
the npx extension instead: `npx -y github:dmauser/financial-services init`.
