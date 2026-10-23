import { readFile, writeFile, mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = fileURLToPath(new URL("../", import.meta.url));
const read = (file) => readFile(path.join(root, file), "utf8");
const write = (file, value) => writeFile(path.join(root, file), value);
const { integrations } = JSON.parse(await read("data/integration-status.json"));
const states = ["In Review", "On Roadmap", "In Progress", "Active"];
const ids = new Set();
for (const integration of integrations) {
  if (ids.has(integration.id) || !states.includes(integration.status) || !integration.markets.length || integration.markets.some((market) => !["US", "CA"].includes(market)) || (integration.beta && integration.status !== "Active")) throw new Error(`Invalid integration: ${integration.id}`);
  ids.add(integration.id);
}
const component = (await read("scripts/integration-status-table.template.jsx")).replace("/* INTEGRATION_DATA */ []", JSON.stringify(integrations));
await mkdir(path.join(root, "snippets"), { recursive: true });
await write("snippets/integration-status-table.jsx", component);

const statusNotes = {
  "In Review": "This integration is being evaluated. Availability has not been announced.",
  "On Roadmap": "This integration is planned for development.",
  "In Progress": "This integration is being built or tested.",
  Active: "This integration is available. Coverage depends on market, product, and account permissions."
};
for (const integration of integrations) {
  const file = `${integration.href.slice(1)}.mdx`;
  let content = await read(file);
  const label = integration.status + (integration.beta ? " (Beta)" : "");
  const message = integration.beta ? "This integration is available in beta. Coverage depends on market, product, and account permissions." : statusNotes[integration.status];
  const note = `<Note>\n**${label}.** ${message} [View integration status](/integrations/status).\n</Note>`;
  content = content.replace(/<Note>[\s\S]*?<\/Note>/, note);
  content = content.replace(/^\| Integration status \|.*\n/gm, "");
  content = content.replace(/^(\| Provider ID \|[^\n]*\n)/m, `$1| Integration status | ${label} |\n`);
  await write(file, content);
}

const config = JSON.parse(await read("docs.json"));
const group = config.navigation.tabs.find((tab) => tab.tab === "Documentation").groups.find((group) => group.group === "Integrations");
group.pages = group.pages.filter((page) => page !== "integrations/status");
group.pages.splice(group.pages.indexOf("integrations/index") + 1, 0, "integrations/status");
await write("docs.json", JSON.stringify(config, null, 2) + "\n");

const catalogNote = `<Note>\nCheck [Integration status](/integrations/status) for current availability. Active integrations marked **Beta** are available in beta. Data coverage depends on the provider, market, product, and account permissions.\n</Note>`;
await write("integrations/index.mdx", (await read("integrations/index.mdx")).replace(/<Note>[\s\S]*?<\/Note>/, catalogNote));
for (const category of new Set(integrations.map((integration) => integration.href.split("/")[2]))) {
  const file = `integrations/${category}/index.mdx`;
  await write(file, (await read(file)).replace(/<Note>[\s\S]*?<\/Note>/, catalogNote));
}

let coverage = await read("data-model/provider-coverage.mdx");
coverage = coverage.replace("Production availability is not verified.", "The draft resource and field mappings have not been verified for production use.");
const byId = new Map(integrations.map((integration) => [integration.id.toLowerCase(), integration]));
coverage = coverage.replace(/<Accordion title="[^"]*" id="([^"]+)">[\s\S]*?<\/Accordion>/g, (block, id) => {
  const integration = byId.get(id);
  if (!integration) return block;
  const label = integration.status + (integration.beta ? " (Beta)" : "");
  return block.replace(/^\| (?:Production status|Integration status) \|.*$/m, `| Integration status | [${label}](/integrations/status) |`);
});
const scopeNote = "Integration status reflects the current AMLOK catalog. Resource and field coverage below remain draft definitions from the source review.";
if (!coverage.includes(scopeNote)) coverage = coverage.replace(/<\/Note>/, `</Note>\n\n${scopeNote}`);
await write("data-model/provider-coverage.mdx", coverage);
console.log(JSON.stringify({ integrations: integrations.length, active: integrations.filter((integration) => integration.status === "Active").length, inReview: integrations.filter((integration) => integration.status === "In Review").length }));
