// financial-services - Copilot CLI extension entrypoint.
//
// This is the file Copilot CLI loads when the extension is installed under
// ~/.copilot/extensions/financial-services/. It resolves the SDK at runtime
// (the SDK is provided by the Copilot CLI host, not bundled with us) and
// joins the session, then delegates registration of specialists/skills/MCPs
// to ./registry.mjs.
//
// Pattern matches the other -desk extensions (compute-desk, relocation-desk):
// pure markdown copied to ~/.copilot/extensions does NOT load - the host
// requires a JS entrypoint that imports @github/copilot-sdk/extension and
// calls joinSession.

import path from 'node:path';
import url from 'node:url';

const HERE = path.dirname(url.fileURLToPath(import.meta.url));

async function loadSdk() {
  try {
    return await import('@github/copilot-sdk/extension');
  } catch (e) {
    try { return await import('@github/copilot-cli-sdk/extension'); }
    catch { throw new Error(`financial-services: copilot SDK not available (${e.message})`); }
  }
}

const sdk = await loadSdk();
const { register } = await import(path.join(HERE, 'registry.mjs'));

await sdk.joinSession({
  name: 'financial-services',
  description:
    'Anthropic Claude for Financial Services - investment banking, equity research, private equity, wealth management, fund admin, and operations workflows.',
  onReady: async (session) => {
    await register(session, { root: HERE });
  },
});
