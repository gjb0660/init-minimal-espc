# Repository Instructions

## Scope

Defines repository-level facts, constraints, layout, and quality checks.

Read `AGENTS.md` for workflow and execution rules.

## Source of Truth

- [specs/knowledge/architecture.md](../specs/knowledge/architecture.md)

## Repository Layout

- Core code MUST stay under `{{CORE_APPLY_TO}}`
- UI code MUST stay under `{{UI_APPLY_TO}}`
- Tests MUST stay under `{{TESTS_APPLY_TO}}`
{{CORE_NAMESPACE_RULE}}
- Docs SHOULD be human-readable export from specs.

## Writing Rules

- MUST use UTF-8 + LF
- SHOULD use English for code,  AGENTS.md, and `.github` files
- SHOULD use bilingual (e.g. Chinese + English headings) for specs and docs

## Git Rules

- MUST NOT rewrite or delete history
- MUST NOT modify files outside workspace scope

## Repository Checks

Before commit, MUST pass:

{{CORE_CHECKS}}
{{UI_CHECKS}}

- `npx markdownlint **/*.md .github/**/*.md`

{{TESTS_CHECKS}}
