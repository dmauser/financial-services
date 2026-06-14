// extension.mjs — Copilot CLI entrypoint for financial-services.
//
// The Copilot CLI host loads this file when the extension is installed under
// ~/.copilot/extensions/financial-services/. It MUST call joinSession() with
// a tools array; pure-markdown extensions do NOT load.
//
// Pattern matches finance-desk / compute-desk / relocation-desk: thin
// wrapper that imports the SDK statically and delegates tool generation
// to ./registry.mjs.

import { joinSession } from "@github/copilot-sdk/extension";
import { tools, presence, inventoryCounts } from "./registry.mjs";

let presenceAnnounced = false;

const session = await joinSession({
    tools,
    hooks: {
        // SessionStart fires on startup / new / resume. Inject the presence
        // note as session-level additional context so the agent knows
        // financial-services exists from turn 1.
        onSessionStart: async () => {
            presenceAnnounced = true;
            return { additionalContext: presence };
        },
        // Belt-and-suspenders: re-announce on the very first user prompt
        // in case onSessionStart didn't fire on this CLI build.
        onUserPromptSubmitted: async (input) => {
            if (presenceAnnounced) return;
            if (!input?.prompt) return;
            presenceAnnounced = true;
            return { additionalContext: presence };
        },
    },
});

await session.log(
    `financial-services loaded — ${inventoryCounts.specialists} specialists, ` +
        `${inventoryCounts.verticals} verticals, ${inventoryCounts.tools} tools`,
);
