// extension.mjs — Copilot CLI entrypoint for financial-services.
//
// The Copilot CLI host loads this file when the extension is installed under
// ~/.copilot/extensions/financial-services/. It MUST call joinSession() with
// a tools array; pure-markdown extensions do NOT load.
//
// Wires three things into the session:
//   - tools     — 169 MCP tools generated from the install tree (registry.mjs)
//   - commands  — 41 slash commands (39 from MAPPING.md + /fs-help + /finance-help)
//   - hooks     — onSessionStart / onUserPromptSubmitted that inject a presence note
//
// CommandHandler returns void; to drive the agent we call session.send(prompt).
// Since the handlers need the session that joinSession() produces, we hold the
// joined session in a closure-captured ref (`sessionRef`) and pass a getter
// (() => sessionRef) into buildCommands().

import { joinSession } from "@github/copilot-sdk/extension";
import { tools, presence, inventoryCounts, buildCommands, commandCount } from "./registry.mjs";

let sessionRef = null;
let presenceAnnounced = false;

const commands = buildCommands(() => sessionRef);

const session = await joinSession({
    tools,
    commands,
    hooks: {
        onSessionStart: async () => {
            presenceAnnounced = true;
            return { additionalContext: presence };
        },
        onUserPromptSubmitted: async (input) => {
            if (presenceAnnounced) return;
            if (!input?.prompt) return;
            presenceAnnounced = true;
            return { additionalContext: presence };
        },
    },
});

sessionRef = session;

await session.log(
    `financial-services loaded — ${inventoryCounts.specialists} specialists, ` +
        `${inventoryCounts.verticals} verticals, ${inventoryCounts.tools} tools, ` +
        `${commandCount} slash commands (try /fs-help)`,
);
