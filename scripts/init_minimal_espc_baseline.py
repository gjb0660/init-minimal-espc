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

    def write_text(self, target: Path, content: str) -> None:
        if target.exists() and not self.overwrite:
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


def rewrite_copilot_instructions(template: str, scan: RepoScan) -> str:
    result: list[str] = []
    for line in template.splitlines():
        stripped = line.strip()
        if stripped.startswith("- Python code MUST stay under"):
            result.append(f"- Core code MUST stay under `{scan.core_apply_to}`")
            continue
        if stripped.startswith("- QML code MUST stay under"):
            result.append(f"- UI code MUST stay under `{scan.ui_apply_to}`")
            continue
        if stripped.startswith("- Tests MUST stay under"):
            result.append(f"- Tests MUST stay under `{scan.tests_apply_to}`")
            continue
        if stripped.startswith("- Python SHOULD NOT include `__init__.py`"):
            if scan.has_python:
                result.append(line)
            continue
        if stripped.startswith("- `uv run pyright --project pyproject.toml`"):
            if scan.has_python:
                result.append(line)
            continue
        if stripped.startswith("- `uv run ruff check src tests`"):
            if scan.has_python:
                result.append(line)
            continue
        if stripped.startswith("- `uv run ruff format src tests`"):
            if scan.has_python:
                result.append(line)
            continue
        if stripped.startswith("- `uv run pyside6-qmllint <qml-files>`"):
            if scan.has_qml:
                result.append(line)
            continue
        if stripped.startswith("- `uv run pyside6-qmlformat -i <qml-files>`"):
            if scan.has_qml:
                result.append(line)
            continue
        if stripped.startswith("- `uv run python -m unittest discover -s tests -p \"test_*.py\" -v`"):
            if scan.has_python:
                result.append(line)
            continue
        result.append(line)
    return _collapse_blank_lines("\n".join(result).rstrip() + "\n")


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


def _todo_lines(domain: str, target: str) -> str:
    return "\n".join(
        [
            f"<!-- TODO(agent-research): Goal: create or refine `{target}`. -->",
            f"<!-- TODO(agent-research): Keep it reusable for AGENTS in `{domain}` scope. -->",
            "<!-- TODO(agent-research): Gather evidence from source, configs, tests, and stable contracts. -->",
            "<!-- TODO(agent-research): Keep out Plan/Progress/Todo execution state. -->",
            "<!-- TODO(agent-research): Remove this TODO block at initialization closeout. -->",
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
        return [
            "Keep runtime behavior configurable.",
            "Avoid hardcoding production environment details.",
            "Preserve separation between execution logic and presentation logic.",
        ]
    if domain == "ui":
        return [
            "Keep UI logic presentation-focused.",
            "Map UI components to ui-specific contracts under `specs/contracts/ui/`.",
            "Do not bypass defined interaction boundaries.",
        ]
    if domain == "tests":
        return [
            "Keep tests deterministic and isolated.",
            "Prefer behavior-first assertions derived from Acceptance criteria.",
            "Avoid test helpers that hide production behavior.",
        ]
    return [
        f"Keep {domain} rules evidence-driven and minimal.",
        "Prefer stable constraints over ad-hoc conventions.",
        "Keep checks aligned with repository-level constraints.",
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


def render_instruction(domain: str, apply_to: str, scan: RepoScan) -> str:
    target = _source_of_truth(domain)
    rel_link = _relative_link(target)

    local_rules = "\n".join(f"- {rule}" for rule in _instruction_local_rules(domain))
    checks = "\n".join(f"- {check}" for check in _instruction_checks(domain, scan))

    body = f"""---
description: \"{_instruction_description(domain)}\"
applyTo: \"{apply_to}\"
---

# {_instruction_title(domain)}

## Scope

{_instruction_scope(domain)}

## Source of Truth

- [{target}]({rel_link})
{_todo_lines(domain, target)}

## Local Rules

{local_rules}

## Local Checks

{checks}
"""

    if domain == "ui":
        ui_note = "A UI file SHOULD be mapped to its ui-specific contract (CamelCase -> kebab-case).\n"
        body = body.replace("## Local Rules\n", f"{ui_note}\n## Local Rules\n")

    if domain not in {"core", "ui", "tests"}:
        extension_note = (
            "Optional contracts extension is allowed only when stable constraints are confirmed.\n"
            "Never reference feature specs as Source of Truth.\n"
        )
        body = body.replace("## Local Rules\n", f"{extension_note}\n## Local Rules\n")

    return body


def initialize_baseline(repo_path: Path, dry_run: bool, overwrite: bool) -> int:
    script_path = Path(__file__).resolve()
    skill_root = script_path.parent.parent
    seed_root = skill_root / "references" / "seed_repo"
    if not seed_root.exists():
        raise FileNotFoundError(f"Seed bundle not found: {seed_root}")

    scan = scan_repo(repo_path)
    writer = Writer(dry_run=dry_run, overwrite=overwrite)

    writer.copy_file(seed_root / "AGENTS.md", repo_path / "AGENTS.md")

    template_copilot = (seed_root / ".github" / "copilot-instructions.md").read_text(
        encoding="utf-8"
    )
    writer.write_text(
        repo_path / ".github" / "copilot-instructions.md",
        rewrite_copilot_instructions(template_copilot, scan),
    )

    writer.write_text(
        repo_path / ".github" / "instructions" / "core.instructions.md",
        render_instruction("core", scan.core_apply_to, scan),
    )
    writer.write_text(
        repo_path / ".github" / "instructions" / "ui.instructions.md",
        render_instruction("ui", scan.ui_apply_to, scan),
    )
    writer.write_text(
        repo_path / ".github" / "instructions" / "tests.instructions.md",
        render_instruction("tests", scan.tests_apply_to, scan),
    )

    for domain in scan.optional_domains:
        writer.write_text(
            repo_path / ".github" / "instructions" / f"{domain}.instructions.md",
            render_instruction(domain, scan.optional_apply_to.get(domain, f"{domain}/**"), scan),
        )

    writer.copy_file(seed_root / "specs" / "index.md", repo_path / "specs" / "index.md")
    writer.copy_file(
        seed_root / "specs" / "features" / "index.md",
        repo_path / "specs" / "features" / "index.md",
    )
    writer.copy_file(
        seed_root / "specs" / "contracts" / "index.md",
        repo_path / "specs" / "contracts" / "index.md",
    )
    writer.copy_file(
        seed_root / "specs" / "knowledge" / "index.md",
        repo_path / "specs" / "knowledge" / "index.md",
    )

    writer.copy_tree(
        seed_root / ".agents" / "skills" / "minimal-espc",
        repo_path / ".agents" / "skills" / "minimal-espc",
    )
    writer.copy_tree(
        seed_root / ".agents" / "skills" / "converge-commit",
        repo_path / ".agents" / "skills" / "converge-commit",
    )

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
