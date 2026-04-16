---
description: "Use when: implementing core runtime and backend logic."
applyTo: "{{APPLY_TO}}"
---

# Core Instructions

## Scope

Applies to core runtime, backend orchestration, and non-UI business logic.

## Source of Truth

- [specs/knowledge/core.md](../../specs/knowledge/core.md)
<!-- TODO(agent-research,source,Q1): What stable responsibilities should `specs/knowledge/core.md` define? -->
<!-- TODO(agent-research,source,Q2): How do code/config/tests provide direct evidence for these boundaries? -->
<!-- TODO(agent-research,source,Q3): When evidence is incomplete, what assumptions must remain hypotheses? -->
<!-- TODO(agent-research,cleanup): After the knowledge doc is completed, can this TODO block be removed? -->

## Local Rules

- MUST keep local rules minimal and evidence-backed.
{{LOCAL_RULES}}
<!-- TODO(agent-research,local-rules,Q1): What core rules are truly stable across features? -->
<!-- TODO(agent-research,local-rules,cleanup): After rules are confirmed, can this TODO block be removed? -->

## Types and Linting

- MUST follow repository-level typing/linting policy.
{{TYPES_AND_LINTING}}
<!-- TODO(agent-research,types-linting,Q1): How should AGENTS fix lint failures by root cause before rerunning checks? -->
<!-- TODO(agent-research,types-linting,cleanup): After policy is documented, can this TODO block be removed? -->

## Local Checks

- MUST run relevant checks before submitting core changes.
{{LOCAL_CHECKS}}
<!-- TODO(agent-research,local-checks,Q1): When should a core check failure block commit? -->
<!-- TODO(agent-research,local-checks,cleanup): After check policy is documented, can this TODO block be removed? -->
