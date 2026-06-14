// financial-services - registers specialists, vertical skills, slash-command
// agents/skills, instructions, and MCP servers with the Copilot CLI host.
//
// Layout (relative to the install root):
//   extensions/financial-services/specialists/<slug>/agents/<slug>.md  - named agents
//   extensions/financial-services/specialists/<slug>/skills/<name>/SKILL.md
//   verticals/<vertical>/skills/<name>/SKILL.md                         - vertical skills
//   commands/agents/<name>/agent.md                                     - high-value /commands as agents
//   commands/skills/<name>/SKILL.md                                     - trigger-only skill wrappers
//   instructions/AGENTS.md                                              - ambient AGENTS.md
//   instructions/instructions/*.instructions.md                         - path-specific
//   mcp/.mcp.json                                                       - runtime config (seeded from .template)
//
// We discover everything by directory walk - no manifest needed.

import { promises as fs } from 'node:fs';
import { existsSync } from 'node:fs';
import path from 'node:path';

async function readJson(p) {
  return JSON.parse(await fs.readFile(p, 'utf8'));
}

async function listDirs(p) {
  if (!existsSync(p)) return [];
  return (await fs.readdir(p, { withFileTypes: true }))
    .filter(d => d.isDirectory())
    .map(d => d.name);
}

async function registerAgent(session, mdPath, opts = {}) {
  if (!existsSync(mdPath)) return;
  const text = await fs.readFile(mdPath, 'utf8');
  await session.registerAgent({ source: mdPath, content: text, ...opts });
}

async function registerSkill(session, skillDir, opts = {}) {
  const skillMd = path.join(skillDir, 'SKILL.md');
  if (!existsSync(skillMd)) return;
  const text = await fs.readFile(skillMd, 'utf8');
  await session.registerSkill({
    source: skillMd,
    name: path.basename(skillDir),
    content: text,
    resourceDir: skillDir,
    ...opts,
  });
}

async function registerInstructions(session, root) {
  const agentsMd = path.join(root, 'instructions', 'AGENTS.md');
  if (existsSync(agentsMd)) {
    await session.registerInstructions({
      source: agentsMd,
      scope: 'agents',
      content: await fs.readFile(agentsMd, 'utf8'),
    });
  }
  const insDir = path.join(root, 'instructions', 'instructions');
  if (existsSync(insDir)) {
    for (const f of await fs.readdir(insDir)) {
      if (!f.endsWith('.instructions.md')) continue;
      const p = path.join(insDir, f);
      await session.registerInstructions({
        source: p,
        scope: 'path',
        content: await fs.readFile(p, 'utf8'),
      });
    }
  }
}

async function registerMcp(session, root) {
  const cfg = path.join(root, 'mcp', '.mcp.json');
  if (!existsSync(cfg)) return;
  const data = await readJson(cfg);
  for (const [name, server] of Object.entries(data.mcpServers || {})) {
    if (server.disabled) continue;
    await session.registerMcpServer({ name, ...server });
  }
}

export async function register(session, { root }) {
  const specRoot = path.join(root, 'extensions', 'financial-services', 'specialists');
  for (const slug of await listDirs(specRoot)) {
    await registerAgent(session, path.join(specRoot, slug, 'agents', `${slug}.md`), {
      tags: ['specialist', slug],
    });
    const skillsDir = path.join(specRoot, slug, 'skills');
    for (const skill of await listDirs(skillsDir)) {
      await registerSkill(session, path.join(skillsDir, skill), {
        tags: ['specialist', slug],
      });
    }
  }

  const verticalRoot = path.join(root, 'verticals');
  for (const v of await listDirs(verticalRoot)) {
    const skillsDir = path.join(verticalRoot, v, 'skills');
    for (const skill of await listDirs(skillsDir)) {
      await registerSkill(session, path.join(skillsDir, skill), { tags: ['vertical', v] });
    }
  }

  const cmdAgentRoot = path.join(root, 'commands', 'agents');
  for (const name of await listDirs(cmdAgentRoot)) {
    await registerAgent(session, path.join(cmdAgentRoot, name, 'agent.md'), {
      tags: ['command-agent', name],
    });
  }

  const cmdSkillRoot = path.join(root, 'commands', 'skills');
  for (const name of await listDirs(cmdSkillRoot)) {
    await registerSkill(session, path.join(cmdSkillRoot, name), { tags: ['command-skill', name] });
  }

  await registerInstructions(session, root);
  await registerMcp(session, root);
}
