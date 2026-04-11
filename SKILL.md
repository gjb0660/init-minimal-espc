---
name: init-minimal-espc
description: Initialize a repository with a minimal ESPC baseline. Use when bootstrapping a fresh project or normalizing governance by asking 3 Socratic questions (goal, scope, acceptance), generating AGENTS/.github/specs skeleton, creating instruction templates with inline research TODO prompts, and seeding minimal-espc + converge-commit.
---

# Init Minimal ESPC

## Goal

Initialize a repository to an executable minimal ESPC baseline while preventing over-design.

## Mandatory Protocol

Before generation, ask exactly these 3 questions and capture explicit answers:

1. Goal: what concrete outcome must initialization unlock immediately?
2. Scope: which repository path is targeted, and should overwrite be enabled?
3. Acceptance: which baseline checks must pass after initialization?

Do not run write mode until the answers are unambiguous.

## Execution

1. Run dry-run first:

```bash
python scripts/init_minimal_espc_baseline.py <repo_path> --dry-run
```

1. Review generated actions, mandatory instructions (`core/ui/tests`), and optional-domain decisions.
1. Run write mode:

```bash
python scripts/init_minimal_espc_baseline.py <repo_path> [--overwrite]
```

1. Have Agent research and author knowledge documents referenced by `Source of Truth` TODO prompts.
1. At initialization closeout, remove inline TODO prompts from generated instructions.

## Generated Baseline

The script generates:

- `AGENTS.md`
- `.github/copilot-instructions.md` (SoT fixed to `specs/knowledge/architecture.md`)
- mandatory instructions:
  - `.github/instructions/core.instructions.md`
  - `.github/instructions/ui.instructions.md`
  - `.github/instructions/tests.instructions.md`
- optional instructions (max 5): `build/deploy/perf/security/api/ops` using dual evidence gate
- `specs/index.md`
- `specs/features/index.md`
- `specs/contracts/index.md`
- `specs/knowledge/index.md`
- `.agents/skills/minimal-espc/**`
- `.agents/skills/converge-commit/**`

The script does not generate knowledge content files. Agent research is required.

## Source-of-Truth Rules

- Each instruction keeps one primary `Source of Truth` reference.
- Fixed mappings:
  - `core -> specs/knowledge/core.md`
  - `ui -> specs/contracts/ui/`
  - `tests -> specs/knowledge/testing.md`
  - `build -> specs/knowledge/building.md`
- Other optional domains map to `specs/knowledge/<domain>.md`.
- Contracts can be added only when stable constraints are confirmed.
- Feature specs must never be referenced as instruction `Source of Truth`.

## Constraints

- Keep first-principles and Occam boundaries.
- Keep repository-specific rewrites minimal (paths and checks only).
- Keep seeded skills unchanged when copied.
- Do not auto-write knowledge conclusions from script heuristics.

## Resources

- `scripts/init_minimal_espc_baseline.py`: scanner + skeleton generator.
- `references/seed_repo/`: seed baseline bundle.
