---
name: init-minimal-espc
description: Initialize a repository with a minimal ESPC baseline. Use when bootstrapping a fresh project or normalizing governance by asking 3 Socratic questions (goal, scope, acceptance), copying `references/seed_repo/**` verbatim, and generating instruction templates with inline research TODO prompts.
---

# Init Minimal ESPC

## Goal

Initialize a repository to an executable minimal ESPC baseline while preventing over-design.

## Mandatory Protocol

Before generation, ask exactly these 3 questions and capture explicit answers:

1. Goal: what concrete outcome must initialization unlock immediately?
2. Scope: where is the target repository path, and should overwrite be enabled?
3. Acceptance: what baseline checks must pass after initialization?

Do not run write mode until the answers are unambiguous.

## Execution

1. Run dry-run first:

```bash
python scripts/init_minimal_espc_baseline.py <repo_path> --dry-run
```

1. Run write mode:

```bash
python scripts/init_minimal_espc_baseline.py <repo_path> [--overwrite]
```

1. Have Agent research and author knowledge documents referenced by `Source of Truth` TODO prompts.
1. At initialization closeout, remove inline TODO prompts from generated instructions.

## Generated Baseline

The script generates:

- all files under `references/seed_repo/**` (copy baseline first, then overlay rendered outputs below)
- `.github/copilot-instructions.md` rendered from placeholder template
- mandatory instructions:
  - `.github/instructions/core.instructions.md`
  - `.github/instructions/ui.instructions.md`
  - `.github/instructions/tests.instructions.md`
  - rendered from seed templates under `references/seed_repo/.github/instructions/`
  - each section uses required baseline + placeholder + inline question-form TODO prompts
- optional instructions (max 5): `build/deploy/perf/security/api/ops` using dual evidence gate
  - rendered from `references/templates/optional.instructions.md`
  - each section uses required baseline + placeholder + inline question-form TODO prompts
  - `Types and Linting` appears only when executable/static checks are detected

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
- Copy content under `references/seed_repo/` verbatim.
- Do not add extra confirmation text for seeded files in script or SKILL.
- Keep script-generated rules minimal and generic by default.
- Keep optional-domain instructions template-driven (`references/templates/optional.instructions.md`).
- Keep TODO density section-graded: `Source of Truth` high, other sections low.
- Keep each generated instruction within a 60-line cognitive budget.
- Do not auto-write knowledge conclusions from script heuristics.

## Resources

- `scripts/init_minimal_espc_baseline.py`: scanner + skeleton generator.
- `references/seed_repo/`: seed baseline bundle.
