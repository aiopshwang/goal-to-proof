#!/usr/bin/env python3
"""Deterministic, dependency-free release validation for Goal to Proof."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit


REQUIRED_CASE_IDS = {
    "T+01", "T+02", "T+03", "T+04", "T+05", "T+06", "T+07", "T+08",
    "T-01", "T-02", "T-03", "T-04", "T-05", "T-06",
    "B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08", "B09", "B10",
}
REQUIRED_GATE_IDS = {"H01", "H02", "H03", "H04", "H05"}
ALLOWED_ORACLES = {
    "command_succeeds",
    "file_absent",
    "file_contains",
    "file_contains_any",
    "file_equals",
    "file_exists",
    "file_is_json",
    "file_not_contains",
    "file_not_contains_any",
    "json_value_equals",
    "max_response_lines",
    "max_response_sentences",
    "only_paths_changed",
    "response_contains_any",
    "response_is_json",
    "response_not_contains",
    "response_not_contains_any",
    "workspace_unchanged",
}
ALLOWED_ORACLE_COMMANDS = {"python", "python3"}
IGNORED_DIRS = {".git", ".venv", "node_modules", "dist", "build", "eval-results", "__pycache__"}
SECRET_PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws-access-key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b"),
    "github-fine-grained-token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{80,255}\b"),
    "openai-key": re.compile(r"\bsk-[A-Za-z0-9_-]{32,255}\b"),
    "slack-token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,255}\b"),
    "npm-auth-token": re.compile(
        r"(?im)^\s*(?://[^\s=]+/:)?_authToken\s*=\s*(?!\$\{|<|REPLACE|YOUR_)[A-Za-z0-9._~+/=-]{16,}\s*$"
    ),
    "pypi-password": re.compile(
        r"(?im)^\s*password\s*=\s*(?!\$\{|<|REPLACE|YOUR_)(?:pypi-)?[A-Za-z0-9._~+/=-]{16,}\s*$"
    ),
}
CASE_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9+_-]{0,63}\Z")


@dataclass(frozen=True)
class Issue:
    severity: str
    code: str
    path: str
    message: str


class Report:
    def __init__(self) -> None:
        self.issues: list[Issue] = []
        self.checks = 0

    def check(self) -> None:
        self.checks += 1

    def add(self, severity: str, code: str, path: Path | str, message: str) -> None:
        self.issues.append(Issue(severity, code, str(path), message))

    def error(self, code: str, path: Path | str, message: str) -> None:
        self.add("error", code, path, message)

    def warning(self, code: str, path: Path | str, message: str) -> None:
        self.add("warning", code, path, message)

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]


class DuplicateKeyError(ValueError):
    pass


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path, report: Report) -> Any | None:
    report.check()
    if not path.is_file():
        report.error("missing-file", path, "required JSON file is missing")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except (OSError, UnicodeError, json.JSONDecodeError, DuplicateKeyError) as exc:
        report.error("invalid-json", path, str(exc))
        return None


def _unquote_yaml_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        if value[0] == '"':
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                pass
        return value[1:-1].replace("''", "'")
    return value


def skill_frontmatter(path: Path, report: Report) -> dict[str, Any] | None:
    report.check()
    if not path.is_file():
        report.error("missing-file", path, "canonical SKILL.md is missing")
        return None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        report.error("unreadable-file", path, str(exc))
        return None
    if not lines or lines[0].strip() != "---":
        report.error("frontmatter", path, "SKILL.md must start with YAML frontmatter")
        return None
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        report.error("frontmatter", path, "SKILL.md frontmatter is not closed")
        return None

    data: dict[str, Any] = {}
    section: str | None = None
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^(\s*)([A-Za-z0-9_-]+):(?:\s*(.*))?$", line)
        if not match:
            report.error("frontmatter", path, f"unsupported frontmatter syntax on line {number}")
            continue
        indent, key, raw = match.groups()
        raw = raw or ""
        if not indent:
            if raw:
                data[key] = _unquote_yaml_scalar(raw)
                section = None
            else:
                data[key] = {}
                section = key
        elif section and isinstance(data.get(section), dict):
            data[section][key] = _unquote_yaml_scalar(raw)
        else:
            report.error("frontmatter", path, f"unexpected indentation on line {number}")
    return data


def is_safe_relative_path(value: str) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts and path.as_posix() == value.replace("\\", "/")


def is_safe_case_id(value: Any) -> bool:
    return isinstance(value, str) and bool(CASE_ID_PATTERN.fullmatch(value))


def _expect(
    condition: bool,
    report: Report,
    code: str,
    path: Path | str,
    message: str,
) -> None:
    report.check()
    if not condition:
        report.error(code, path, message)


def validate_skill(root: Path, report: Report) -> tuple[str | None, str | None]:
    path = root / "skills/goal-to-proof/SKILL.md"
    frontmatter = skill_frontmatter(path, report)
    if frontmatter is None:
        return None, None
    name = frontmatter.get("name")
    version = frontmatter.get("metadata", {}).get("version") if isinstance(frontmatter.get("metadata"), dict) else None
    description = frontmatter.get("description", "")
    _expect(name == "goal-to-proof", report, "skill-name", path, "skill name must be goal-to-proof")
    _expect(isinstance(description, str) and "Use when" in description and "Do not use" in description,
            report, "skill-description", path, "description must state positive and negative activation boundaries")
    _expect(frontmatter.get("license") == "MIT", report, "skill-license", path, "skill license must be MIT")
    _expect(isinstance(frontmatter.get("metadata"), dict), report, "skill-metadata", path, "metadata mapping is required")
    _expect(isinstance(version, str) and bool(re.fullmatch(r"\d+\.\d+\.\d+", version or "")),
            report, "skill-version", path, "metadata.version must be a semantic version")

    openai_path = root / "skills/goal-to-proof/agents/openai.yaml"
    report.check()
    if not openai_path.is_file():
        report.error("missing-file", openai_path, "OpenAI interface metadata is missing")
    else:
        text = openai_path.read_text(encoding="utf-8")
        _expect("$goal-to-proof" in text, report, "default-prompt", openai_path,
                "default_prompt must explicitly mention $goal-to-proof")
        _expect(bool(re.search(r"allow_implicit_invocation:\s*true\b", text, re.IGNORECASE)),
                report, "implicit-invocation", openai_path, "implicit invocation must be enabled")
    return name if isinstance(name, str) else None, version if isinstance(version, str) else None


def validate_manifests(root: Path, report: Report, skill_name: str | None, skill_version: str | None) -> None:
    codex_path = root / ".codex-plugin/plugin.json"
    claude_path = root / ".claude-plugin/plugin.json"
    codex_market_path = root / ".agents/plugins/marketplace.json"
    claude_market_path = root / ".claude-plugin/marketplace.json"
    codex = load_json(codex_path, report)
    claude = load_json(claude_path, report)
    codex_market = load_json(codex_market_path, report)
    claude_market = load_json(claude_market_path, report)

    versions: dict[str, str] = {}
    for label, path, data in (("codex", codex_path, codex), ("claude", claude_path, claude)):
        if not isinstance(data, dict):
            continue
        _expect(data.get("name") == skill_name == "goal-to-proof", report, "manifest-name", path,
                "plugin and canonical skill names must match")
        version = data.get("version")
        _expect(isinstance(version, str) and bool(re.fullmatch(r"\d+\.\d+\.\d+", version or "")),
                report, "manifest-version", path, "plugin version must be semantic")
        if isinstance(version, str):
            versions[label] = version
        _expect(data.get("license") == "MIT", report, "manifest-license", path, "plugin license must be MIT")
        _expect(data.get("repository") == "https://github.com/aiopshwang/goal-to-proof", report,
                "manifest-repository", path, "repository URL must target the public canonical repository")

    if isinstance(codex, dict):
        _expect(codex.get("skills") == "./skills/", report, "codex-skills-path", codex_path,
                "Codex manifest must expose ./skills/")
        interface = codex.get("interface")
        _expect(isinstance(interface, dict), report, "codex-interface", codex_path, "interface metadata is required")
        if isinstance(interface, dict):
            prompts = interface.get("defaultPrompt")
            _expect(isinstance(prompts, list) and len(prompts) >= 3 and all(isinstance(item, str) for item in prompts),
                    report, "starter-prompts", codex_path, "at least three starter prompts are required")

    if isinstance(codex_market, dict):
        plugins = codex_market.get("plugins")
        _expect(isinstance(plugins, list) and len(plugins) == 1, report, "codex-marketplace", codex_market_path,
                "Codex marketplace must expose exactly one plugin")
        if isinstance(plugins, list) and plugins and isinstance(plugins[0], dict):
            plugin = plugins[0]
            _expect(plugin.get("name") == "goal-to-proof", report, "codex-marketplace-name", codex_market_path,
                    "marketplace plugin name must be goal-to-proof")
            _expect(plugin.get("source") == {"source": "url", "url": "./"}, report,
                    "codex-marketplace-source", codex_market_path, "marketplace source must point to the repository root")

    if isinstance(claude_market, dict):
        plugins = claude_market.get("plugins")
        _expect(isinstance(plugins, list) and len(plugins) == 1, report, "claude-marketplace", claude_market_path,
                "Claude marketplace must expose exactly one plugin")
        if isinstance(plugins, list) and plugins and isinstance(plugins[0], dict):
            plugin = plugins[0]
            _expect(plugin.get("name") == "goal-to-proof", report, "claude-marketplace-name", claude_market_path,
                    "marketplace plugin name must be goal-to-proof")
            _expect(plugin.get("source") == "./", report, "claude-marketplace-source", claude_market_path,
                    "marketplace source must point to the repository root")
            version = plugin.get("version")
            if isinstance(version, str):
                versions["claude-marketplace"] = version

    if isinstance(skill_version, str):
        versions["skill"] = skill_version

    citation_path = root / "CITATION.cff"
    if citation_path.is_file():
        citation_text = citation_path.read_text(encoding="utf-8")
        match = re.search(r"^version:\s*['\"]?(\d+\.\d+\.\d+)['\"]?\s*$", citation_text, re.MULTILINE)
        _expect(match is not None, report, "citation-version", citation_path,
                "CITATION.cff must contain a semantic version")
        if match:
            versions["citation"] = match.group(1)

    changelog_path = root / "CHANGELOG.md"
    if changelog_path.is_file():
        changelog_text = changelog_path.read_text(encoding="utf-8")
        match = re.search(r"^## \[(\d+\.\d+\.\d+)\]", changelog_text, re.MULTILINE)
        _expect(match is not None, report, "changelog-version", changelog_path,
                "CHANGELOG.md must contain a released semantic-version heading")
        if match:
            versions["changelog"] = match.group(1)

    site_path = root / "docs/index.html"
    if site_path.is_file():
        site_text = site_path.read_text(encoding="utf-8")
        match = re.search(r"['\"]version['\"]\s*:\s*['\"](\d+\.\d+\.\d+)['\"]", site_text)
        _expect(match is not None, report, "site-version", site_path,
                "docs/index.html must expose a semantic version in structured data")
        if match:
            versions["site"] = match.group(1)

    report.check()
    if versions and len(set(versions.values())) != 1:
        rendered = ", ".join(f"{key}={value}" for key, value in sorted(versions.items()))
        report.error("version-mismatch", root, f"all published versions must match: {rendered}")


def _validate_oracle(check: Any, path: Path, report: Report, case_id: str) -> None:
    if not isinstance(check, dict):
        report.error("eval-oracle", path, f"{case_id}: oracle checks must be objects")
        return
    kind = check.get("type")
    _expect(kind in ALLOWED_ORACLES, report, "eval-oracle-type", path,
            f"{case_id}: unsupported oracle type {kind!r}")
    if "path" in check:
        _expect(is_safe_relative_path(check["path"]), report, "eval-path", path,
                f"{case_id}: unsafe oracle path {check['path']!r}")
    if kind == "only_paths_changed":
        paths = check.get("paths")
        _expect(isinstance(paths, list) and paths and all(is_safe_relative_path(item) for item in paths),
                report, "eval-path", path, f"{case_id}: only_paths_changed requires safe paths")
    if kind == "command_succeeds":
        argv = check.get("argv")
        _expect(isinstance(argv, list) and argv and all(isinstance(item, str) and item for item in argv),
                report, "eval-command", path, f"{case_id}: command oracle must use a non-empty argument array")
        if isinstance(argv, list) and argv:
            _expect(argv[0] in ALLOWED_ORACLE_COMMANDS, report, "eval-command", path,
                    f"{case_id}: command {argv[0]!r} is not allow-listed")
    if kind == "json_value_equals":
        _expect(isinstance(check.get("key"), str) and bool(check["key"]), report,
                "eval-oracle", path, f"{case_id}: json_value_equals requires a non-empty key")
        _expect("value" in check, report, "eval-oracle", path,
                f"{case_id}: json_value_equals requires a value")


def validate_evals(root: Path, report: Report) -> None:
    hard_path = root / "evals/hard_gates.json"
    trigger_path = root / "evals/trigger_cases.json"
    behavior_path = root / "evals/behavior_cases.json"
    hard = load_json(hard_path, report)
    trigger = load_json(trigger_path, report)
    behavior = load_json(behavior_path, report)

    gates: dict[str, dict[str, Any]] = {}
    if isinstance(hard, dict) and isinstance(hard.get("gates"), list):
        for gate in hard["gates"]:
            if isinstance(gate, dict) and isinstance(gate.get("id"), str):
                if gate["id"] in gates:
                    report.error("eval-duplicate-gate", hard_path, f"duplicate gate {gate['id']}")
                gates[gate["id"]] = gate
        _expect(set(gates) == REQUIRED_GATE_IDS, report, "eval-gate-coverage", hard_path,
                f"hard gates must be exactly {sorted(REQUIRED_GATE_IDS)}")
        for gate_id, gate in gates.items():
            _expect(all(isinstance(gate.get(field), str) and gate[field].strip() for field in ("name", "rule", "failure")),
                    report, "eval-gate-fields", hard_path, f"{gate_id}: name, rule, and failure are required")
    else:
        report.error("eval-gates", hard_path, "gates must be a JSON array")

    all_cases: list[tuple[Path, dict[str, Any]]] = []
    for path, data in ((trigger_path, trigger), (behavior_path, behavior)):
        if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("cases"), list):
            report.error("eval-suite", path, "suite must have schema_version 1 and a cases array")
            continue
        for case in data["cases"]:
            if not isinstance(case, dict):
                report.error("eval-case", path, "each case must be an object")
                continue
            all_cases.append((path, case))

    ids = [case.get("id") for _, case in all_cases]
    _expect(len(ids) == len(set(ids)), report, "eval-duplicate-case", root / "evals", "case IDs must be unique")
    _expect(set(ids) == REQUIRED_CASE_IDS, report, "eval-case-coverage", root / "evals",
            f"eval matrix must contain exactly 24 required cases; got {sorted(str(item) for item in ids)}")
    kinds = {"trigger_positive": 0, "trigger_negative": 0, "behavior": 0}

    for path, case in all_cases:
        case_id = case.get("id", "<missing>")
        _expect(is_safe_case_id(case_id), report, "eval-case-id", path,
                f"unsafe case ID {case_id!r}; IDs must be one short filesystem-safe component")
        kind = case.get("kind")
        if kind in kinds:
            kinds[kind] += 1
        else:
            report.error("eval-kind", path, f"{case_id}: invalid case kind {kind!r}")
        for field in ("title", "prompt"):
            _expect(isinstance(case.get(field), str) and bool(case[field].strip()), report,
                    "eval-field", path, f"{case_id}: {field} must be non-empty")
        setup = case.get("setup")
        _expect(isinstance(setup, dict) and isinstance(setup.get("files"), list), report,
                "eval-setup", path, f"{case_id}: setup.files must be an array")
        setup_paths: set[str] = set()
        if isinstance(setup, dict) and isinstance(setup.get("files"), list):
            for fixture in setup["files"]:
                if not isinstance(fixture, dict):
                    report.error("eval-fixture", path, f"{case_id}: each fixture must be an object")
                    continue
                fixture_path = fixture.get("path")
                _expect(is_safe_relative_path(fixture_path), report, "eval-path", path,
                        f"{case_id}: unsafe fixture path {fixture_path!r}")
                _expect(isinstance(fixture.get("content"), str), report, "eval-fixture", path,
                        f"{case_id}: fixture content must be text")
                if isinstance(fixture_path, str):
                    _expect(fixture_path not in setup_paths, report, "eval-fixture", path,
                            f"{case_id}: duplicate fixture path {fixture_path}")
                    setup_paths.add(fixture_path)

        expected = case.get("expected")
        _expect(isinstance(expected, dict), report, "eval-expected", path, f"{case_id}: expected object is required")
        if not isinstance(expected, dict):
            continue
        activation = expected.get("skill_activation")
        required_activation = {
            "trigger_positive": "implicit",
            "trigger_negative": "not_expected",
            "behavior": "explicit",
        }.get(kind)
        _expect(activation == required_activation, report, "eval-activation", path,
                f"{case_id}: expected skill_activation {required_activation!r}")
        prompt = case.get("prompt", "")
        if kind == "behavior":
            _expect("$goal-to-proof" in prompt, report, "eval-explicit-prompt", path,
                    f"{case_id}: explicit behavior prompt must mention $goal-to-proof")
        else:
            _expect("$goal-to-proof" not in prompt, report, "eval-trigger-prompt", path,
                    f"{case_id}: trigger prompt must not explicitly name the skill")
        for field in ("requirements", "prohibitions"):
            values = expected.get(field)
            _expect(isinstance(values, list) and values and all(isinstance(item, str) and item.strip() for item in values),
                    report, "eval-expectation", path, f"{case_id}: {field} must be a non-empty string array")
        hard_gates = expected.get("hard_gates")
        _expect(isinstance(hard_gates, list) and all(item in gates for item in hard_gates), report,
                "eval-gate-reference", path, f"{case_id}: hard_gates contains an unknown ID")
        oracle = expected.get("oracle")
        _expect(isinstance(oracle, dict), report, "eval-oracle", path, f"{case_id}: oracle object is required")
        if isinstance(oracle, dict):
            for group in ("workspace", "response"):
                checks = oracle.get(group)
                _expect(isinstance(checks, list), report, "eval-oracle", path,
                        f"{case_id}: oracle.{group} must be an array")
                if isinstance(checks, list):
                    for check in checks:
                        _validate_oracle(check, path, report, str(case_id))
            manual = oracle.get("manual")
            _expect(isinstance(manual, list) and all(isinstance(item, str) and item.strip() for item in manual),
                    report, "eval-oracle", path, f"{case_id}: oracle.manual must be a string array")

    _expect(kinds == {"trigger_positive": 8, "trigger_negative": 6, "behavior": 10},
            report, "eval-kind-coverage", root / "evals", f"unexpected case counts: {kinds}")
    referenced_gates = {
        gate
        for _, case in all_cases
        for gate in case.get("expected", {}).get("hard_gates", [])
        if isinstance(gate, str)
    }
    _expect(referenced_gates == REQUIRED_GATE_IDS, report, "eval-gate-coverage", root / "evals",
            "every hard gate must be exercised by at least one case")


def iter_release_entries(root: Path) -> Iterable[Path]:
    for directory, dirnames, filenames in os.walk(root):
        base = Path(directory)
        retained_dirs: list[str] = []
        for name in sorted(dirnames):
            if name in IGNORED_DIRS:
                continue
            path = base / name
            if path.is_symlink():
                yield path
            else:
                retained_dirs.append(name)
        dirnames[:] = retained_dirs
        for name in sorted(filenames):
            yield base / name


def iter_scannable_files(root: Path) -> Iterable[Path]:
    for path in iter_release_entries(root):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            if path.stat().st_size <= 2_000_000:
                yield path
        except OSError:
            continue


def _local_link_target(source: Path, raw_target: str, root: Path) -> Path | None:
    target = raw_target.strip().strip("<>")
    if not target or target.startswith("#") or "{{" in target:
        return None
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or target.startswith("//"):
        return None
    decoded = unquote(parsed.path)
    if not decoded or decoded.startswith("/"):
        return None
    return (source.parent / decoded).resolve()


def validate_local_links(root: Path, report: Report) -> None:
    markdown_pattern = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
    html_pattern = re.compile(r"(?:href|src)\s*=\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
    for path in iter_scannable_files(root):
        if path.suffix.lower() not in {".md", ".html"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            report.error("unreadable-file", path.relative_to(root), str(exc))
            continue
        matches = markdown_pattern.findall(text) if path.suffix.lower() == ".md" else html_pattern.findall(text)
        for raw_target in matches:
            target = _local_link_target(path, raw_target, root)
            if target is None:
                continue
            report.check()
            try:
                target.relative_to(root.resolve())
            except ValueError:
                report.error("link-escape", path.relative_to(root), f"local link escapes repository: {raw_target}")
                continue
            if not target.exists():
                report.error("broken-local-link", path.relative_to(root), f"missing local target: {raw_target}")


def validate_secrets_and_source_hygiene(root: Path, report: Report) -> None:
    forbidden_parts = {"ai_session", "chat_exports", "conversation_exports", "raw_sessions"}
    for path in iter_release_entries(root):
        relative = path.relative_to(root)
        report.check()
        if path.is_symlink():
            report.error("release-symlink", relative, "symbolic links are not allowed in the release tree")
            continue
        if not path.is_file():
            continue
        if any(part.lower() in forbidden_parts for part in relative.parts):
            report.error("raw-source-data", relative, "private source-session material must not be published")
        if path.suffix.lower() in {".jsonl", ".sqlite", ".db", ".har"}:
            report.error("raw-source-data", relative, "session/database capture files are not allowed in the release")
        try:
            if path.stat().st_size > 2_000_000:
                continue
        except OSError as exc:
            report.error("unreadable-file", relative, str(exc))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            report.error("unreadable-file", relative, str(exc))
            continue
        for name, pattern in SECRET_PATTERNS.items():
            report.check()
            if pattern.search(text):
                report.error("secret-pattern", relative, f"possible {name} detected")


def validate_required_release_files(root: Path, report: Report) -> None:
    required = [
        "README.md", "README.ko.md", "LICENSE", "CHANGELOG.md", "PRIVACY.md", "TERMS.md",
        "SECURITY.md", "SUPPORT.md", "CITATION.cff", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md",
        "docs/index.html", "evals/README.md", "evals/ab_protocol.md",
        "scripts/run_ab_eval.py", "tests/test_validate.py", ".github/workflows/ci.yml",
    ]
    for relative in required:
        path = root / relative
        _expect(path.is_file(), report, "missing-release-file", Path(relative), "required release file is missing")

    workflow = root / ".github/workflows/ci.yml"
    if workflow.is_file():
        text = workflow.read_text(encoding="utf-8")
        _expect("python scripts/validate.py --strict" in text, report, "ci-validator", workflow.relative_to(root),
                "CI must run the deterministic release validator")
        _expect("python -m unittest discover" in text, report, "ci-tests", workflow.relative_to(root),
                "CI must run the standard-library test suite")

    gitignore = root / ".gitignore"
    if gitignore.is_file():
        ignored = {line.strip() for line in gitignore.read_text(encoding="utf-8").splitlines()}
        _expect("eval-results/" in ignored, report, "eval-output-ignore", gitignore.relative_to(root),
                "generated live-evaluation results must be ignored")

    for relative in ("scripts/run_ab_eval.py", "evals/ab_protocol.md"):
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in ("--auth-file", "auth.json"):
            _expect(forbidden not in text, report, "credential-file-interface", path.relative_to(root),
                    f"public runner materials must not accept or copy credential files ({forbidden})")


def validate_repository(root: Path) -> Report:
    root = root.resolve()
    report = Report()
    skill_name, skill_version = validate_skill(root, report)
    validate_manifests(root, report, skill_name, skill_version)
    validate_evals(root, report)
    validate_required_release_files(root, report)
    validate_local_links(root, report)
    validate_secrets_and_source_hygiene(root, report)
    return report


def _render_text(report: Report) -> str:
    lines = []
    for issue in sorted(report.issues, key=lambda item: (item.severity, item.path, item.code, item.message)):
        lines.append(f"{issue.severity.upper()} [{issue.code}] {issue.path}: {issue.message}")
    status = "PASS" if not report.errors else "FAIL"
    lines.append(
        f"{status}: {report.checks} checks, {len(report.errors)} errors, {len(report.warnings)} warnings"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true", dest="json_output", help="emit a machine-readable report")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    args = parser.parse_args(argv)

    report = validate_repository(args.root)
    if args.json_output:
        payload = {
            "status": "pass" if not report.errors else "fail",
            "checks": report.checks,
            "errors": len(report.errors),
            "warnings": len(report.warnings),
            "issues": [asdict(issue) for issue in report.issues],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_render_text(report))
    return 1 if report.errors or (args.strict and report.warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
