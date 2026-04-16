---
description: "Use when: writing tests."
applyTo: "{{APPLY_TO}}"
---

# Test Instructions

## Scope

Applies to unit and integration tests.

## Source of Truth

- [specs/knowledge/testing.md](../../specs/knowledge/testing.md)
<!-- TODO(agent-research,source,Q1): What testing invariants keep behavior verification stable in this repository? -->
<!-- TODO(agent-research,source,Q2): How do existing tests show canonical assertion style and boundaries? -->
<!-- TODO(agent-research,source,Q3): Where do flaky risks appear, and when are they evidence-backed vs speculative? -->
<!-- TODO(agent-research,cleanup): After testing knowledge is completed, can this TODO block be removed? -->

## Local Rules

- MUST keep test rules tied to deterministic behavior verification.
{{LOCAL_RULES}}
<!-- TODO(agent-research,local-rules,Q1): What testing rules are truly stable across suites? -->
<!-- TODO(agent-research,local-rules,cleanup): After rules are confirmed, can this TODO block be removed? -->

## Local Checks

- MUST run relevant checks before submitting test changes.
{{LOCAL_CHECKS}}
<!-- TODO(agent-research,local-checks,Q1): When should a test check failure block commit? -->
<!-- TODO(agent-research,local-checks,cleanup): After check policy is documented, can this TODO block be removed? -->
