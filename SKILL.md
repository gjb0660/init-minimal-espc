---
name: init-minimal-espc
description: Initialize a repository with a minimal ESPC baseline. Use when bootstrapping a fresh project or normalizing governance by asking 3 Socratic questions (goal, scope, acceptance), copying `references/seed_repo/**` verbatim, and generating instruction templates with inline research TODO prompts.
---

# Init Minimal ESPC

## Goal

Initialize a repository to an executable minimal ESPC baseline while preventing over-design.

## Layer Contract

### Layer A: Meta-Skill Layer

- Owns generation protocol, placeholders, and rendering behavior.
- Uses generic domain terms (`core/ui/tests`) for stable abstraction.
- MUST NOT generate knowledge from heuristics.
- MUST keep TODO prompts as research scaffolding and require cleanup after first convergence.
- MUST ask: if one generation rule is removed, which invariant breaks?

### Layer B: Project-Rules Layer

- Owns generated repository rules under `.github/*instructions*`.
- Output files are execution rules, not template implementation notes.
- May use concrete stack terms (`Python/QML/...`) when evidence exists.
- MUST keep Source of Truth mapping explicit and singular by default.
- MUST ask: does each rule have evidence, boundary, or blocking value?

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
  - `Types and Linting` appears only when domain-path evidence detects executable/static checks

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
- Keep script-generated rules minimal and generic in Layer A.
- Keep Layer B rules executable: keep normative lines, trim explanation noise.
- Keep optional-domain instructions template-driven (`references/templates/optional.instructions.md`).
- Keep TODO density section-graded: `Source of Truth` high, other sections low.
- Keep 60-line cognitive budget as output acceptance target (not script auto-trimming gate).
- Keep optional checks/types domain-scoped; do not inject stack checks from unrelated paths.
- Do not auto-write knowledge conclusions from script heuristics.

## Socratic Self-Check

Before finalizing initialization output, the Agent SHOULD challenge assumptions:

1. Which generated rule would fail open if removed?
2. Does each `MUST/SHOULD` constrain behavior, or just restate preference?
3. Is every blocking check tied to the domain path that will run it?
4. Does any Source of Truth line point to unstable or feature-specific content?
5. Are TODO prompts still needed, or already replaceable by verified knowledge/contracts?

## Resources

- `scripts/init_minimal_espc_baseline.py`: scanner + skeleton generator.
- `references/seed_repo/`: seed baseline bundle.
