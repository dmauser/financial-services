#!/usr/bin/env node
// financial-services — GitHub Copilot CLI extension installer
//
// Mirrors the -desk installer pattern (compute-desk, finance-desk, relocation-desk):
// drops a self-contained extension into ~/.copilot/extensions/financial-services/
// with the minimal extension.mjs + registry.mjs entrypoints Copilot CLI needs to
// load specialists, skills, and MCP servers.
//
// Subcommands:
//   init                    Install into ~/.copilot/extensions/financial-services/
//   init --project          Install into ./.copilot/extensions/financial-services/ (project-local)
//   uninstall               Remove the installed extension
//   status                  Show install location, version, MCP enable state
//   mcp list                Show all 12 connectors and their enable state
//   mcp enable <name>       Flip a connector to enabled (still requires API key)
//   mcp disable <name>      Flip a connector back to disabled
//   help                    Show help

import { promises as fs } from 'node:fs';
import { existsSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import url from 'node:url';
import process from 'node:process';

const SELF = path.dirname(url.fileURLToPath(import.meta.url));
const ROOT = path.resolve(SELF, '..');
const PKG = JSON.parse(await fs.readFile(path.join(ROOT, 'package.json'), 'utf8'));
const NAME = PKG.name;

const args = process.argv.slice(2);

function targetDir({ project }) {
  return project
    ? path.resolve(process.cwd(), '.copilot', 'extensions', NAME)
    : path.resolve(os.homedir(), '.copilot', 'extensions', NAME);
}

async function copyDir(src, dst) {
  await fs.mkdir(dst, { recursive: true });
  for (const entry of await fs.readdir(src, { withFileTypes: true })) {
    const s = path.join(src, entry.name);
    const d = path.join(dst, entry.name);
    if (entry.isDirectory()) await copyDir(s, d);
    else if (entry.isFile()) await fs.copyFile(s, d);
  }
}

async function writeMeta(dst) {
  await fs.writeFile(
    path.join(dst, '.install-meta.json'),
    JSON.stringify(
      { name: NAME, version: PKG.version, installedAt: new Date().toISOString(), source: ROOT },
      null,
      2
    ) + '\n'
  );
}

async function init({ project }) {
  const dst = targetDir({ project });
  console.log(`[${NAME}] installing to ${dst}`);
  await fs.mkdir(dst, { recursive: true });
  for (const entry of [
    'extension.mjs',
    'registry.mjs',
    'extensions',
    'verticals',
    'commands',
    'mcp',
    'instructions',
    '.copilot-plugin',
    'RECOMMENDATIONS.md',
    'README.md',
    'CHANGELOG.md',
  ]) {
    const src = path.join(ROOT, entry);
    if (!existsSync(src)) continue;
    const target = path.join(dst, entry);
    const stat = await fs.stat(src);
    if (stat.isDirectory()) await copyDir(src, target);
    else await fs.copyFile(src, target);
  }
  await writeMeta(dst);
  console.log(`[${NAME}] installed v${PKG.version}`);
  console.log(`[${NAME}] next: open Copilot CLI in any repo and run /env to confirm load.`);
  console.log(`[${NAME}] enable an MCP: npx ${NAME} mcp enable daloopa`);
}

async function uninstall({ project }) {
  const dst = targetDir({ project });
  if (!existsSync(dst)) {
    console.log(`[${NAME}] not installed at ${dst}`);
    return;
  }
  await fs.rm(dst, { recursive: true, force: true });
  console.log(`[${NAME}] removed ${dst}`);
}

async function status({ project }) {
  const dst = targetDir({ project });
  const metaPath = path.join(dst, '.install-meta.json');
  if (!existsSync(metaPath)) {
    console.log(`[${NAME}] not installed at ${dst}`);
    return;
  }
  const meta = JSON.parse(await fs.readFile(metaPath, 'utf8'));
  console.log(`[${NAME}] installed v${meta.version} at ${dst}`);
  console.log(`[${NAME}] source: ${meta.source}`);
  console.log(`[${NAME}] installed at: ${meta.installedAt}`);
  await mcpList({ project, quiet: false });
}

async function mcpFile({ project }) {
  const dst = targetDir({ project });
  return path.join(dst, 'mcp', '.mcp.json');
}

async function loadMcp({ project }) {
  const file = await mcpFile({ project });
  if (!existsSync(file)) {
    const dst = targetDir({ project });
    const template = path.join(dst, 'mcp', '.mcp.json.template');
    if (!existsSync(template)) throw new Error(`no MCP template at ${template}`);
    await fs.copyFile(template, file);
  }
  return JSON.parse(await fs.readFile(file, 'utf8'));
}

async function saveMcp({ project }, data) {
  const file = await mcpFile({ project });
  await fs.writeFile(file, JSON.stringify(data, null, 2) + '\n');
}

async function mcpList({ project, quiet }) {
  const data = await loadMcp({ project });
  const rows = Object.entries(data.mcpServers || {}).map(([name, cfg]) => ({
    name,
    enabled: cfg.disabled === true ? 'disabled' : 'enabled',
    url: cfg.url || cfg.command || '',
  }));
  if (!quiet) console.log(`[${NAME}] MCP connectors:`);
  for (const r of rows) {
    const mark = r.enabled === 'enabled' ? '[x]' : '[ ]';
    console.log(`  ${mark} ${r.name.padEnd(14)} ${r.enabled.padEnd(8)} ${r.url}`);
  }
}

async function mcpToggle({ project }, name, disabled) {
  const data = await loadMcp({ project });
  if (!data.mcpServers || !data.mcpServers[name]) {
    console.error(`[${NAME}] unknown MCP connector: ${name}`);
    process.exit(1);
  }
  data.mcpServers[name].disabled = disabled;
  await saveMcp({ project }, data);
  console.log(`[${NAME}] ${name} -> ${disabled ? 'disabled' : 'enabled'}`);
  if (!disabled) {
    console.log(`[${NAME}] reminder: this connector requires a provider subscription/API key. See provider docs.`);
  }
}

function help() {
  console.log(`${NAME} v${PKG.version} - GitHub Copilot CLI extension installer

Usage:
  npx ${NAME} <command> [options]

Commands:
  init                  Install into ~/.copilot/extensions/${NAME}/
  init --project        Install into ./.copilot/extensions/${NAME}/ (this repo only)
  uninstall             Remove the installed extension
  uninstall --project   Remove project-local install
  status                Show install location, version, and MCP enable state
  mcp list              List all 12 MCP connectors and their state
  mcp enable <name>     Enable an MCP connector (still requires API key)
  mcp disable <name>    Disable an MCP connector
  help                  Show this message

Examples:
  npx -y github:dmauser/financial-services init
  npx ${NAME} mcp enable daloopa
  npx ${NAME} mcp enable factset
  npx ${NAME} status

After install, restart Copilot CLI and run /env to confirm extension/skills/agents loaded.
See RECOMMENDATIONS.md for day-in-the-life workflows.
`);
}

const project = args.includes('--project');
const positional = args.filter(a => !a.startsWith('--'));

try {
  switch (positional[0]) {
    case 'init': await init({ project }); break;
    case 'uninstall': await uninstall({ project }); break;
    case 'status': await status({ project }); break;
    case 'mcp': {
      const sub = positional[1];
      if (sub === 'list') await mcpList({ project, quiet: false });
      else if (sub === 'enable') await mcpToggle({ project }, positional[2], false);
      else if (sub === 'disable') await mcpToggle({ project }, positional[2], true);
      else { help(); process.exit(1); }
      break;
    }
    case 'help':
    case undefined:
      help();
      break;
    default:
      console.error(`[${NAME}] unknown command: ${positional[0]}`);
      help();
      process.exit(1);
  }
} catch (e) {
  console.error(`[${NAME}] error:`, e.message);
  process.exit(1);
}
