---
name: subagent-explore
description: Launches an exploration subagent to map code structure, locate relevant files, and summarize architecture quickly. Use when the user asks to explore an unfamiliar codebase, find where systems are implemented, or requests broad codebase discovery.
---

# Subagent Explore

## Quick Start

Use this skill when the task is broad discovery rather than a narrow symbol lookup.

1. Decide whether the request is broad enough for a subagent.
2. Launch one exploration subagent with clear scope and expected output.
3. For large repos or multiple independent questions, launch up to 3 subagents in parallel.
4. Return a concise synthesis with file paths and actionable next steps.

## When To Use

Use an exploration subagent when the user asks things like:
- "How is this codebase structured?"
- "Where does auth/reporting/importing happen?"
- "Map the flow from input to output."
- "Find all major modules and responsibilities."

Do not use this skill for:
- Exact text lookup (use direct search)
- Single-file edits
- Straightforward, narrow tasks with obvious file targets

## Subagent Prompt Template

Use this template when launching:

```text
Task: Explore the codebase area related to <topic>.

Goals:
1) Identify key files and directories
2) Explain data/control flow
3) List main symbols (classes/functions/modules) and responsibilities
4) Note unknowns or ambiguity

Return format:
- Scope searched
- Key findings (bulleted)
- Important file paths
- Open questions
- Suggested next steps

Thoroughness: <quick|medium|very thorough>
```

## Execution Guidance

- Start with `quick` when the user asks a high-level question.
- Use `medium` when the user needs actionable file-level guidance.
- Use `very thorough` only for architecture deep dives.
- Keep prompts focused on one domain per subagent (auth, reporting, UI, etc.).
- Ask subagents to include exact paths and short reasoning.

## Output Format

Present results in this order:
1. What was explored
2. Main findings
3. File paths to inspect next
4. Risks or unknowns
5. Recommended next action

## Additional Resources

- Usage examples: [examples.md](examples.md)
