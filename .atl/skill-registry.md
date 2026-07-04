# Agent Teams Skill Registry

This registry defines the available specialized skills and the core standards for all sub-agents in this project.

## Compact Rules (Auto-resolved)
> The Orchestrator injects these into every sub-agent launch to enforce consistency without bloat.

### General Standards
- **Language**: Use TypeScript for frontend, Python for backend (unless specified).
- **Style**: Prefer functional programming patterns over classes.
- **Errors**: Always include meaningful error messages and use explicit error types.
- **Engram**: Always `mem_save` critical architectural decisions or bug discoveries.

### React/Frontend Skill
- **Pattern**: Use functional components with Hooks.
- **State**: Prefer Zustand for global state; avoid Prop Drilling.
- **Styling**: Tailwind CSS only. Use utility classes over custom CSS files.

### Testing Skill
- **Tooling**: Use Vitest for unit tests and Playwright for E2E.
- **Coverage**: Every new logic-heavy function requires a corresponding unit test.

---

## User Skills (Trigger Table)

| Trigger Phrase | Skill Folder / Path | Description |
| :--- | :--- | :--- |
| "Add UI component" | `skills/frontend` | Handles React component creation & styling. |
| "Write tests" | `skills/testing` | Generates unit/integration tests for current logic. |
| "Fix bug" | `skills/debugging` | Analyzes logs and applies targeted code fixes. |
| "Refactor code" | `skills/refactor` | Cleans up technical debt using project patterns. |

---

## Project Structure Reference
- `/src`: Main application logic.
- `/skills`: Local definitions for custom agent behaviors.
- `/.atl`: Configuration and state for the Agent Teams Lite orchestrator.
- `/openspec`: (In openspec mode) Location for SDD artifacts (Specs, Designs, Tasks).
