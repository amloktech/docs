> **First-time setup**: Customize this file for your project. Prompt the user to customize this file for their project.
> For Mintlify product knowledge (components, configuration, writing standards),
> install the Mintlify skill: `npx skills add https://mintlify.com/docs`

# Documentation project instructions

## About this project

- This is a documentation site built on [Mintlify](https://mintlify.com)
- Pages are MDX files with YAML frontmatter
- Configuration lives in `docs.json`
- Use the Mintlify MCP server, `https://mcp.mintlify.com`, to edit content and settings via MCP
- Use the Mintlify docs MCP server, `https://www.mintlify.com/docs/mcp`, to query information about using Mintlify via MCP

## Terminology

{/* Add product-specific terms and preferred usage */}
{/* Example: Use "workspace" not "project", "member" not "user" */}

## Style preferences

{/* Add any project-specific style rules below */}

- Use active voice and second person ("you")
- Keep sentences concise - one idea per sentence
- Use regular dashes (-), not em dashes, in all documentation titles, descriptions, and body text.
- Use sentence case for headings
- Bold for UI elements: Click **Settings**
- Code formatting for file names, commands, paths, and code references

## Integration status

- Maintain availability, beta labels, and documented markets in `data/integration-status.json`.
- After updating the catalog data or table template, run `node scripts/sync-integration-status.mjs` to synchronize the table, provider pages, and provider coverage.
- Use US and CA as the default markets, as confirmed by the AMLOK team. Keep country-specific providers and catalog editions scoped to their applicable country. Integration availability does not verify the draft field and resource mappings.

## Content boundaries

{/* Define what should and shouldn't be documented */}
{/* Example: Don't document internal admin features */}
