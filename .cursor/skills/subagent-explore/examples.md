# Subagent Explore Examples

## Example 1: Architecture Discovery

User request:
"Help me understand this project's architecture."

Suggested subagent task focus:
- Target full repo
- Thoroughness: medium
- Output: module map, request/data flow, top-level responsibilities

## Example 2: Feature Location

User request:
"Where is report export implemented?"

Suggested subagent task focus:
- Target reporting/export areas
- Thoroughness: quick
- Output: candidate files, main functions, call chain

## Example 3: Parallel Exploration

User request:
"Map auth and billing systems."

Suggested approach:
- Launch 2 subagents in parallel:
  - Subagent A: auth domain
  - Subagent B: billing domain
- Thoroughness: medium
- Merge results into one combined summary with shared touchpoints

## Example 4: Pre-Implementation Recon

User request:
"Add caching to report generation."

Suggested subagent task focus:
- Explore report generation pipeline first
- Thoroughness: medium
- Output: where cache can be injected, likely invalidation points, risk areas
