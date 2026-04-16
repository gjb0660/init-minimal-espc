from __future__ import annotations

import argparse
import os
import shutil
from dataclasses import dataclass
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    ".tmp",
    "dist",
}

CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".swift",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".rb",
    ".php",
    ".scala",
    ".qml",
    ".vue",
    ".svelte",
}

UI_EXTENSIONS = {".qml", ".tsx", ".jsx", ".vue", ".svelte", ".css", ".scss", ".less"}
UI_TOKENS = {"ui", "frontend", "front-end", "client", "web", "views", "components", "qml"}
TEST_TOKENS = {"test", "tests", "testing", "spec", "specs"}

OPTIONAL_DOMAIN_ORDER = ["build", "deploy", "perf", "security", "api", "ops"]
MANDATORY_DOMAIN_TEMPLATES = {
    "core": "core.instructions.md",
    "ui": "ui.instructions.md",
    "tests": "tests.instructions.md",
}
OPTIONAL_INSTRUCTION_TEMPLATE = Path("references") / "templates" / "optional.instructions.md"

OPTIONAL_DOMAIN_RULES: dict[str, dict[str, list[str]]] = {
    "build": {
        "dir_tokens": ["build", "scripts", "packaging", ".github/workflows", ".github/actions", "tools"],
        "responsibility_keywords": [
            "build",
            "package",
            "pyproject.toml",
            "setup.py",
            "makefile",
            "cmakelists",
            "build.gradle",
            "pom.xml",
            "webpack",
            "vite",
            "rollup",
        ],
    },
    "deploy": {
        "dir_tokens": ["deploy", "deployment", "infra", "helm", "k8s", "kubernetes", "terraform"],
        "responsibility_keywords": [
            "deploy",
            "dockerfile",
            "docker-compose",
            "helm",
            "k8s",
            "kubernetes",
            "terraform",
            "ansible",
            "release",
        ],
    },
    "perf": {
        "dir_tokens": ["perf", "performance", "benchmark", "benchmarks", "profiling"],
        "responsibility_keywords": ["perf", "performance", "benchmark", "profile", "latency", "throughput"],
    },
    "security": {
        "dir_tokens": ["security", "auth", "secrets", "iam", "policy", "policies"],
        "responsibility_keywords": ["security", "auth", "oauth", "jwt", "tls", "ssl", "secret", "vuln"],
    },
    "api": {
        "dir_tokens": ["api", "apis", "openapi", "swagger", "graphql", "proto", "protos", "schema", "schemas"],
        "responsibility_keywords": ["openapi", "swagger", "graphql", "endpoint", "route", "grpc", "proto", "api"],
    },
    "ops": {
        "dir_tokens": ["ops", "runbook", "runbooks", "monitoring", "observability", "sre", "alerts", "logging"],
        "responsibility_keywords": ["runbook", "monitor", "observability", "alert", "log", "incident", "ops", "sre"],
    },
}


@dataclass
class RepoScan:
    rel_files: list[Path]
    directory_paths: set[str]
    directory_parts: set[str]
    has_python: bool
    has_qml: bool
    has_tests: bool
    core_apply_to: str
    ui_apply_to: str
    tests_apply_to: str
    optional_domains: list[str]
    optional_apply_to: dict[str, str]
    optional_evidence: dict[str, str]


class Writer:
    def __init__(self, dry_run: bool, overwrite: bool) -> None:
        self.dry_run = dry_run
        self.overwrite = overwrite
        self.actions: list[str] = []

    def write_text(self, target: Path, content: str, force: bool = False) -> None:
        if target.exists() and not (self.overwrite or force):
            self.actions.append(f"SKIP  {target} (exists)")
            return
        self.actions.append(f"WRITE {target}")
        if self.dry_run:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")

    def copy_file(self, source: Path, target: Path) -> None:
        if target.exists() and not self.overwrite:
            self.actions.append(f"SKIP  {target} (exists)")
            return
        self.actions.append(f"COPY  {source} -> {target}")
        if self.dry_run:
            return
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    def copy_tree(self, source_root: Path, target_root: Path) -> None:
        for source in source_root.rglob("*"):
            rel = source.relative_to(source_root)
            target = target_root / rel
            if source.is_dir():
                if not self.dry_run:
                    target.mkdir(parents=True, exist_ok=True)
                continue
            self.copy_file(source, target)


def _walk_files(repo_path: Path) -> list[Path]:
    files: list[Path] = []
    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        root_path = Path(root)
        for filename in filenames:
            files.append(root_path / filename)
    return files


def _common_parent(paths: list[Path], repo_path: Path) -> Path | None:
    if not paths:
        return None
    rel_parents = [list(path.relative_to(repo_path).parent.parts) for path in paths]
    common = rel_parents[0]
    for parts in rel_parents[1:]:
        i = 0
        while i < len(common) and i < len(parts) and common[i] == parts[i]:
            i += 1
        common = common[:i]
        if not common:
            break
    if not common:
        return Path(".")
    return Path(*common)


def _to_scope_pattern(common_parent: Path | None, fallback: str) -> str:
    if common_parent is None:
        return fallback
    if str(common_parent) == ".":
        return "**"
    return f"{common_parent.as_posix()}/**"


def _collect_dir_data(rel_files: list[Path]) -> tuple[set[str], set[str]]:
    dir_paths: set[str] = set()
    dir_parts: set[str] = set()
    for rel in rel_files:
        parent = rel.parent
        while str(parent) != ".":
            path_text = parent.as_posix().lower()
            dir_paths.add(path_text)
            for part in parent.parts:
                dir_parts.add(part.lower())
            parent = parent.parent
    return dir_paths, dir_parts


def _is_test_path(rel: Path) -> bool:
    parts = [part.lower() for part in rel.parts]
    if any(token in TEST_TOKENS for token in parts):
        return True
    name = rel.name.lower()
    return name.startswith("test_") or name.endswith("_test.py") or name.endswith(".spec.ts") or name.endswith(".spec.js")


def _is_ui_path(rel: Path) -> bool:
    parts = [part.lower() for part in rel.parts]
    if any(token in UI_TOKENS for token in parts):
        return True
    return rel.suffix.lower() in UI_EXTENSIONS


def _match_dir_paths_for_token(token: str, dir_paths: set[str], dir_parts: set[str]) -> set[str]:
    token_lower = token.lower().strip("/")
    matches: set[str] = set()

    if "/" in token_lower:
        for path in dir_paths:
            if path == token_lower or path.endswith(f"/{token_lower}"):
                matches.add(path)
        return matches

    if token_lower not in dir_parts:
        return matches

    for path in dir_paths:
        if token_lower in path.split("/"):
            matches.add(path)
    return matches


def _common_prefix_path(paths: list[str]) -> str:
    if not paths:
        return ""
    prefix_parts = paths[0].split("/")
    for path in paths[1:]:
        parts = path.split("/")
        i = 0
        while i < len(prefix_parts) and i < len(parts) and prefix_parts[i] == parts[i]:
            i += 1
        prefix_parts = prefix_parts[:i]
        if not prefix_parts:
            return ""
    return "/".join(prefix_parts)


def _optional_apply_to(domain: str, matched_dirs: set[str]) -> str:
    if not matched_dirs:
        return f"{domain}/**"
    common = _common_prefix_path(sorted(matched_dirs))
    if common:
        return f"{common}/**"
    return f"{domain}/**"


def _detect_domain_hits(
    rel_files: list[Path], dir_paths: set[str], dir_parts: set[str]
) -> tuple[list[str], dict[str, str], dict[str, str]]:
    lower_paths = [rel.as_posix().lower() for rel in rel_files]
    selected: list[str] = []
    evidence: dict[str, str] = {}
    apply_to: dict[str, str] = {}

    for domain in OPTIONAL_DOMAIN_ORDER:
        rule = OPTIONAL_DOMAIN_RULES[domain]
        dir_tokens = rule["dir_tokens"]
        keywords = rule["responsibility_keywords"]

        matched_dirs: set[str] = set()
        for token in dir_tokens:
            matched_dirs.update(_match_dir_paths_for_token(token, dir_paths, dir_parts))

        dir_hit = bool(matched_dirs)

        duty_hit = any(keyword in path for keyword in keywords for path in lower_paths)

        if dir_hit and duty_hit:
            selected.append(domain)
            evidence[domain] = "dir+responsibility"
            apply_to[domain] = _optional_apply_to(domain, matched_dirs)
        if len(selected) >= 5:
            break

    return selected, evidence, apply_to


def scan_repo(repo_path: Path) -> RepoScan:
    files = _walk_files(repo_path)
    rel_files = [path.relative_to(repo_path) for path in files]
    dir_paths, dir_parts = _collect_dir_data(rel_files)

    core_files: list[Path] = []
    ui_files: list[Path] = []
    test_files: list[Path] = []
    has_python = False
    has_qml = False

    for rel in rel_files:
        suffix = rel.suffix.lower()
        if suffix == ".py":
            has_python = True
        if suffix == ".qml":
            has_qml = True

        if suffix not in CODE_EXTENSIONS:
            continue
        if _is_test_path(rel):
            test_files.append(rel)
            continue
        if _is_ui_path(rel):
            ui_files.append(rel)
            continue
        if rel.parts and rel.parts[0].lower() in {".github", ".agents"}:
            continue
        core_files.append(rel)

    has_tests = bool(test_files) or (repo_path / "tests").exists()

    core_parent = _common_parent([repo_path / rel for rel in core_files], repo_path)
    ui_parent = _common_parent([repo_path / rel for rel in ui_files], repo_path)
    tests_parent = _common_parent([repo_path / rel for rel in test_files], repo_path)

    src_exists = (repo_path / "src").exists()
    if src_exists:
        core_default = "src/**"
    elif (repo_path / "backend").exists():
        core_default = "backend/**"
    elif (repo_path / "app").exists():
        core_default = "app/**"
    else:
        core_default = "src/**"

    if ui_parent is None:
        if (repo_path / "src" / "ui").exists():
            ui_default = "src/ui/**"
        elif (repo_path / "ui").exists():
            ui_default = "ui/**"
        elif (repo_path / "frontend").exists():
            ui_default = "frontend/**"
        else:
            ui_default = "src/**/ui/**" if src_exists else "ui/**"
    else:
        ui_default = "src/**/ui/**"

    tests_default = "tests/**"

    core_apply_to = _to_scope_pattern(core_parent, core_default)
    ui_apply_to = _to_scope_pattern(ui_parent, ui_default)
    tests_apply_to = _to_scope_pattern(tests_parent, tests_default)

    if tests_parent is None:
        tests_apply_to = tests_default

    optional_domains, optional_evidence, optional_apply_to = _detect_domain_hits(
        rel_files, dir_paths, dir_parts
    )

    return RepoScan(
        rel_files=rel_files,
        directory_paths=dir_paths,
        directory_parts=dir_parts,
        has_python=has_python,
        has_qml=has_qml,
        has_tests=has_tests,
        core_apply_to=core_apply_to,
        ui_apply_to=ui_apply_to,
        tests_apply_to=tests_apply_to,
        optional_domains=optional_domains,
        optional_apply_to=optional_apply_to,
        optional_evidence=optional_evidence,
    )


def _collapse_blank_lines(text: str) -> str:
    out = text
    while "\n\n\n" in out:
        out = out.replace("\n\n\n", "\n\n")
    return out


def render_copilot_instructions_from_template(seed_root: Path, scan: RepoScan) -> str:
    template_path = seed_root / ".github" / "copilot-instructions.md"
    if not template_path.exists():
        raise FileNotFoundError(f"Copilot template missing: {template_path}")

    python_checks = ""
    if scan.has_python:
        python_checks = "\n".join(
            [
                "- `uv run pyright --project pyproject.toml`",
                "- `uv run ruff check src tests`",
                "- `uv run ruff format src tests`",
            ]
        )

    ui_checks = ""
    if scan.has_qml:
        ui_checks = "\n".join(
            [
                "- `uv run pyside6-qmllint <qml-files>`",
                "- `uv run pyside6-qmlformat -i <qml-files>`",
            ]
        )

    test_checks = ""
    if scan.has_python:
        test_checks = '- `uv run python -m unittest discover -s tests -p "test_*.py" -v`'

    python_namespace_rule = ""
    if scan.has_python:
        python_namespace_rule = "- Python SHOULD NOT include `__init__.py` in namespace packages"

    replacements = {
        "{{CORE_APPLY_TO}}": scan.core_apply_to,
        "{{UI_APPLY_TO}}": scan.ui_apply_to,
        "{{TESTS_APPLY_TO}}": scan.tests_apply_to,
        "{{PYTHON_NAMESPACE_RULE}}": python_namespace_rule,
        "{{PYTHON_CHECKS}}": python_checks,
        "{{UI_CHECKS}}": ui_checks,
        "{{TEST_CHECKS}}": test_checks,
    }

    content = template_path.read_text(encoding="utf-8")
    for key, value in replacements.items():
        content = content.replace(key, value)
    return _collapse_blank_lines(content.rstrip() + "\n")


def _source_of_truth(domain: str) -> str:
    if domain == "core":
        return "specs/knowledge/core.md"
    if domain == "ui":
        return "specs/contracts/ui/"
    if domain == "tests":
        return "specs/knowledge/testing.md"
    if domain == "build":
        return "specs/knowledge/building.md"
    return f"specs/knowledge/{domain}.md"


def _relative_link(target: str) -> str:
    return f"../../{target}"


def _source_todo_lines(domain: str, target: str) -> str:
    return "\n".join(
        [
            f"<!-- TODO(agent-research,source,Q1): What stable boundaries should `{target}` define for `{domain}`? -->",
            "<!-- TODO(agent-research,source,Q2): How do files/tests/configs provide direct evidence for this source? -->",
            "<!-- TODO(agent-research,source,Q3): When evidence is incomplete, what assumptions must stay hypotheses? -->",
            "<!-- TODO(agent-research,cleanup): After the knowledge/contract doc is complete, can this TODO block be removed? -->",
        ]
    )


def _local_rules_todo_lines(domain: str) -> str:
    return "\n".join(
        [
            f"<!-- TODO(agent-research,local-rules,Q1): What `{domain}` local rules are truly stable across features? -->",
            "<!-- TODO(agent-research,local-rules,cleanup): After rules are confirmed, can this TODO block be removed? -->",
        ]
    )


def _types_todo_lines(domain: str) -> str:
    return "\n".join(
        [
            f"<!-- TODO(agent-research,types-linting,Q1): How should AGENTS fix lint/type failures by root cause in `{domain}` before rerunning checks? -->",
            "<!-- TODO(agent-research,types-linting,cleanup): After policy is documented, can this TODO block be removed? -->",
        ]
    )


def _checks_todo_lines(domain: str) -> str:
    return "\n".join(
        [
            f"<!-- TODO(agent-research,local-checks,Q1): When should a check failure block commit for `{domain}`? -->",
            "<!-- TODO(agent-research,local-checks,cleanup): After check policy is documented, can this TODO block be removed? -->",
        ]
    )


def _instruction_title(domain: str) -> str:
    if domain == "core":
        return "Core Instructions"
    if domain == "ui":
        return "UI Instructions"
    if domain == "tests":
        return "Test Instructions"
    return f"{domain.capitalize()} Instructions"


def _instruction_description(domain: str) -> str:
    if domain == "core":
        return "Use when: implementing core runtime and backend logic."
    if domain == "ui":
        return "Use when: modifying UI components and interaction behavior."
    if domain == "tests":
        return "Use when: writing or updating tests."
    return f"Use when: implementing {domain}-related concerns."


def _instruction_scope(domain: str) -> str:
    if domain == "core":
        return "Applies to core runtime, backend orchestration, and non-UI business logic."
    if domain == "ui":
        return "Applies to UI components and interaction paths."
    if domain == "tests":
        return "Applies to unit and integration tests."
    return f"Applies to {domain}-related implementation and validation concerns."


def _instruction_local_rules(domain: str) -> list[str]:
    if domain == "core":
        return ["SHOULD keep runtime behavior configurable where applicable."]
    if domain == "ui":
        return ["SHOULD map UI changes to ui-specific contracts."]
    if domain == "tests":
        return ["SHOULD derive assertions directly from Acceptance criteria."]
    return [
        "SHOULD keep rules minimal and evidence-driven.",
        "SHOULD align domain rules with repository-level constraints.",
    ]


def _instruction_checks(domain: str, scan: RepoScan) -> list[str]:
    if domain == "core" and scan.has_python:
        return [
            "`uv run pyright --project pyproject.toml`",
            "`uv run ruff check`",
            "fix findings before `uv run ruff format`",
        ]
    if domain == "ui" and scan.has_qml:
        return [
            "`uv run pyside6-qmllint`",
            "fix findings before `uv run pyside6-qmlformat -i`",
        ]
    if domain == "tests":
        if scan.has_python:
            return ["`uv run python -m unittest discover -s tests -p \"test_*.py\" -v`"]
        return ["Use repository-level test checks defined in `.github/copilot-instructions.md`."]
    return ["Use repository-level checks defined in `.github/copilot-instructions.md`."]


def _instruction_types_and_linting(domain: str, scan: RepoScan) -> list[str]:
    if domain == "core":
        if scan.has_python:
            return [
                "SHOULD keep `pyright` at 0 errors, 0 warnings, 0 infos.",
                "SHOULD fix findings from root cause; do not suppress local code issues.",
                "SHOULD NOT add `# pyright: ignore[...]`, `# type: ignore`, or `# noqa` to bypass findings.",
                "SHOULD avoid `Any`; prefer concrete types, `Protocol`, and minimal typed surfaces.",
                "MUST NOT relax global settings in `pyproject.toml` as a workaround.",
            ]
        return ["Use repository-level typing/linting policy in `.github/copilot-instructions.md`."]

    if domain == "ui":
        if scan.has_qml:
            return [
                "SHOULD keep `pyside6-qmllint` at 0 errors, 0 warnings.",
                "SHOULD fix findings from root-cause; do not suppress findings.",
                "SHOULD NOT add `// qmllint disable ...` to bypass findings.",
            ]
        return ["Use repository-level typing/linting policy in `.github/copilot-instructions.md`."]

    return [
        "SHOULD fix lint/type failures at root cause before retry.",
        "SHOULD NOT bypass failures with suppress/ignore pragmas.",
    ]


def _optional_domain_checks(scan: RepoScan) -> list[str]:
    checks: list[str] = []
    if scan.has_python:
        checks.extend(
            [
                "`uv run pyright --project pyproject.toml`",
                "`uv run ruff check`",
            ]
        )
    if scan.has_qml:
        checks.extend(
            [
                "`uv run pyside6-qmllint`",
            ]
        )
    return checks


def _optional_domain_types_and_linting(scan: RepoScan) -> list[str]:
    if not _optional_domain_checks(scan):
        return []
    lines = [
        "SHOULD fix lint/type failures at root cause before retry.",
        "SHOULD NOT bypass failures with suppress/ignore pragmas.",
    ]
    if scan.has_python:
        lines.append("SHOULD avoid blanket `# type: ignore` or `# noqa` in domain changes.")
    if scan.has_qml:
        lines.append("SHOULD avoid `// qmllint disable ...` suppressions in domain changes.")
    return lines


def _bullet_lines(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _render_template(content: str, replacements: dict[str, str]) -> str:
    rendered = content
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return _collapse_blank_lines(rendered.rstrip() + "\n")


def _compress_todo_lines(lines: list[str]) -> list[str]:
    compressed: list[str] = []
    seen_groups: set[str] = set()
    for line in lines:
        stripped = line.strip()
        if "<!-- TODO(" not in stripped:
            compressed.append(line)
            continue
        if "cleanup" in stripped:
            compressed.append(line)
            continue
        marker = "agent-research,"
        idx = stripped.find(marker)
        if idx == -1:
            compressed.append(line)
            continue
        rest = stripped[idx + len(marker) :]
        group = rest.split(",", 1)[0]
        if group in seen_groups:
            continue
        seen_groups.add(group)
        compressed.append(line)
    return compressed


def _drop_noncritical_description(lines: list[str]) -> list[str]:
    if len(lines) <= 60:
        return lines
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            out.append(line)
            continue
        if stripped.startswith(("#", "-", "<!--")):
            out.append(line)
            continue
        # Preserve only heading/bullet/todo/link-driven lines when shrinking.
        continue
    return out


def _enforce_instruction_line_cap(text: str, cap: int = 60) -> str:
    lines = text.rstrip("\n").splitlines()
    if len(lines) <= cap:
        return _collapse_blank_lines(text.rstrip() + "\n")

    lines = _compress_todo_lines(lines)
    if len(lines) <= cap:
        return _collapse_blank_lines("\n".join(lines).rstrip() + "\n")

    lines = _drop_noncritical_description(lines)
    if len(lines) <= cap:
        return _collapse_blank_lines("\n".join(lines).rstrip() + "\n")

    # Final fallback: trim non-cleanup TODOs from bottom-up.
    idx = len(lines) - 1
    while len(lines) > cap and idx >= 0:
        stripped = lines[idx].strip()
        if "<!-- TODO(" in stripped and "cleanup" not in stripped:
            del lines[idx]
        idx -= 1
    return _collapse_blank_lines("\n".join(lines).rstrip() + "\n")


def render_mandatory_instruction_from_template(
    seed_root: Path, domain: str, apply_to: str, scan: RepoScan
) -> str:
    template_name = MANDATORY_DOMAIN_TEMPLATES[domain]
    template_path = seed_root / ".github" / "instructions" / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Mandatory instruction template missing: {template_path}")

    content = template_path.read_text(encoding="utf-8")
    rendered = _render_template(
        content,
        {
            "{{APPLY_TO}}": apply_to,
            "{{LOCAL_RULES}}": _bullet_lines(_instruction_local_rules(domain)),
            "{{TYPES_AND_LINTING}}": _bullet_lines(_instruction_types_and_linting(domain, scan)),
            "{{LOCAL_CHECKS}}": _bullet_lines(_instruction_checks(domain, scan)),
        },
    )
    return _enforce_instruction_line_cap(rendered)


def render_optional_instruction_from_template(
    skill_root: Path, domain: str, apply_to: str, scan: RepoScan
) -> str:
    template_path = skill_root / OPTIONAL_INSTRUCTION_TEMPLATE
    if not template_path.exists():
        raise FileNotFoundError(f"Optional instruction template missing: {template_path}")

    target = _source_of_truth(domain)
    rel_link = _relative_link(target)
    content = template_path.read_text(encoding="utf-8")
    optional_checks = _optional_domain_checks(scan)
    local_checks = optional_checks or _instruction_checks(domain, scan)
    optional_types = _optional_domain_types_and_linting(scan)
    types_section = ""
    if optional_types:
        types_section = (
            "## Types and Linting\n\n"
            "- MUST follow repository-level typing/linting policy.\n"
            f"{_bullet_lines(optional_types)}\n"
            f"{_types_todo_lines(domain)}\n"
        )

    rendered = _render_template(
        content,
        {
            "{{DESCRIPTION}}": _instruction_description(domain),
            "{{APPLY_TO}}": apply_to,
            "{{TITLE}}": _instruction_title(domain),
            "{{SCOPE}}": _instruction_scope(domain),
            "{{SOURCE_OF_TRUTH_PATH}}": target,
            "{{SOURCE_OF_TRUTH_LINK}}": rel_link,
            "{{SOURCE_TODO}}": _source_todo_lines(domain, target),
            "{{LOCAL_RULES}}": _bullet_lines(_instruction_local_rules(domain)),
            "{{LOCAL_RULES_TODO}}": _local_rules_todo_lines(domain),
            "{{TYPES_AND_LINTING_SECTION}}": types_section,
            "{{LOCAL_CHECKS}}": _bullet_lines(local_checks),
            "{{LOCAL_CHECKS_TODO}}": _checks_todo_lines(domain),
        },
    )
    return _enforce_instruction_line_cap(rendered)


def initialize_baseline(repo_path: Path, dry_run: bool, overwrite: bool) -> int:
    script_path = Path(__file__).resolve()
    skill_root = script_path.parent.parent
    seed_root = skill_root / "references" / "seed_repo"
    if not seed_root.exists():
        raise FileNotFoundError(f"Seed bundle not found: {seed_root}")

    scan = scan_repo(repo_path)
    writer = Writer(dry_run=dry_run, overwrite=overwrite)

    generated: list[tuple[Path, str]] = [
        (
            repo_path / ".github" / "copilot-instructions.md",
            render_copilot_instructions_from_template(seed_root, scan),
        ),
        (
            repo_path / ".github" / "instructions" / "core.instructions.md",
            render_mandatory_instruction_from_template(seed_root, "core", scan.core_apply_to, scan),
        ),
        (
            repo_path / ".github" / "instructions" / "ui.instructions.md",
            render_mandatory_instruction_from_template(seed_root, "ui", scan.ui_apply_to, scan),
        ),
        (
            repo_path / ".github" / "instructions" / "tests.instructions.md",
            render_mandatory_instruction_from_template(seed_root, "tests", scan.tests_apply_to, scan),
        ),
    ]

    for domain in scan.optional_domains:
        generated.append(
            (
                repo_path / ".github" / "instructions" / f"{domain}.instructions.md",
                render_optional_instruction_from_template(
                    skill_root,
                    domain,
                    scan.optional_apply_to.get(domain, f"{domain}/**"),
                    scan,
                ),
            )
        )

    preexisting: dict[Path, bool] = {target: target.exists() for target, _ in generated}

    writer.copy_tree(seed_root, repo_path)

    for target, content in generated:
        if overwrite or not preexisting[target]:
            writer.write_text(target, content, force=True)

    mode = "DRY-RUN" if dry_run else "WRITE"
    print(f"[{mode}] repo={repo_path}")
    for action in writer.actions:
        print(action)

    print("\nSummary:")
    print(f"- core applyTo: {scan.core_apply_to}")
    print(f"- ui applyTo: {scan.ui_apply_to}")
    print(f"- tests applyTo: {scan.tests_apply_to}")
    if scan.optional_domains:
        print(f"- optional domains: {', '.join(scan.optional_domains)}")
        for domain in scan.optional_domains:
            print(
                f"  - {domain}: {scan.optional_evidence.get(domain, 'dir+responsibility')}, "
                f"applyTo={scan.optional_apply_to.get(domain, f'{domain}/**')}"
            )
    else:
        print("- optional domains: none (core/ui/tests only)")

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize minimal ESPC baseline for a target repository."
    )
    parser.add_argument("repo_path", help="Target repository path.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview generated operations without writing files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files when targets already exist.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_path = Path(args.repo_path).resolve()
    if not repo_path.exists():
        raise FileNotFoundError(f"Target repository does not exist: {repo_path}")
    if not repo_path.is_dir():
        raise NotADirectoryError(f"Target path is not a directory: {repo_path}")
    return initialize_baseline(
        repo_path=repo_path,
        dry_run=bool(args.dry_run),
        overwrite=bool(args.overwrite),
    )


if __name__ == "__main__":
    raise SystemExit(main())
