# OpenSpec (SDD artifacts)

This repo uses **OpenSpec** mode: specs, designs, tasks, and per-change state live under `openspec/changes/<change-name>/`.

Per change, use a folder `openspec/changes/<kebab-case-name>/` with:

| Phase | File |
|--------|------|
| DAG / recovery | `state.yaml` |
| Explore | `explore.md` |
| Proposal | `proposal.md` |
| Spec | `spec.md` |
| Design | `design.md` |
| Tasks | `tasks.md` |
| Apply | `apply-progress.md` |
| Verify | `verify-report.md` |
| Archive | `archive-report.md` |

Recovery: read `openspec/changes/*/state.yaml` when resuming SDD after context loss.
