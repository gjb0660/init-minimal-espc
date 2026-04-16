---
description: "Use when: modifying UI components and interaction behavior."
applyTo: "{{APPLY_TO}}"
---

# UI Instructions

## Scope

Applies to UI components and interaction paths.

## Source of Truth

- [specs/contracts/ui/](../../specs/contracts/ui/)
<!-- TODO(agent-research,source,Q1): What UI behaviors in `specs/contracts/ui/` are stable and reusable? -->
<!-- TODO(agent-research,source,Q2): How do components map to these contracts with direct evidence? -->
<!-- TODO(agent-research,source,Q3): When interaction evidence is weak, what assumptions must stay provisional? -->
<!-- TODO(agent-research,cleanup): After ui contracts are completed, can this TODO block be removed? -->

A UI file SHOULD be mapped to its ui-specific contract (CamelCase -> kebab-case).

## Local Rules

- MUST keep UI rules constrained by ui-specific contracts.
{{LOCAL_RULES}}
<!-- TODO(agent-research,local-rules,Q1): What UI rules are truly stable across screens/components? -->
<!-- TODO(agent-research,local-rules,cleanup): After rules are confirmed, can this TODO block be removed? -->

## Types and Linting

- MUST follow repository-level typing/linting policy.
{{TYPES_AND_LINTING}}
<!-- TODO(agent-research,types-linting,Q1): How should AGENTS fix lint failures by root cause before rerunning checks? -->
<!-- TODO(agent-research,types-linting,cleanup): After policy is documented, can this TODO block be removed? -->

## Local Checks

- MUST run relevant checks before submitting UI changes.
{{LOCAL_CHECKS}}
<!-- TODO(agent-research,local-checks,Q1): When should a UI check failure block commit? -->
<!-- TODO(agent-research,local-checks,cleanup): After check policy is documented, can this TODO block be removed? -->
