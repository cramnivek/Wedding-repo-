/* Launch a browser that can reach the deployed site.
 *
 * This container's egress goes through an Anthropic proxy that terminates TLS
 * with its own CA, which Chromium does not carry in its store. Rather than
 * turning certificate checking off wholesale, the four interception CAs in
 * /root/.ccr/ca-bundle.crt are pinned by SPKI — verification stays on for
 * every other certificate, so a genuinely bad one still fails.
 *
 * Outside this container none of it is needed: drop the args and it is a
 * plain chromium.launch().
 *
 *   const { launch } = require('./livehost.cjs');
 */
const { chromium } = require('playwright-core');
const PINS = [
  'PS48cX347wDVcRynzq+DFqswl2PLNE1sG6uQvxMCOS0=',
  'KnP1OnzHv/y42eRQmbGwoYTHcSJF448m6CU5mdngwKk=',
  'gBdItbWylHhTkoJDRwIiMuweY/qX4F0bJmLNs5wosUQ=',
  'L+/CZomxifpzjiAVG11S0bTbaTopj+c49s0rBjjSC6A='
].join(',');

module.exports.launch = () => chromium.launch({
  executablePath: process.env.CHROME_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  args: ['--ignore-certificate-errors-spki-list=' + PINS]
});
