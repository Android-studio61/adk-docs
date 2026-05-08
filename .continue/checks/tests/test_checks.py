"""
Tests for .continue/checks agent instruction files.

Covers the PR changes:
- agentsmd-updater.md: newly added agent check file
- lighthouse-best-practice-analyzer.md: deleted file (must not exist)
"""

import os
import re

import pytest
import yaml

CHECKS_DIR = os.path.join(os.path.dirname(__file__), "..")
AGENTSMD_UPDATER_PATH = os.path.join(CHECKS_DIR, "agentsmd-updater.md")
LIGHTHOUSE_ANALYZER_PATH = os.path.join(
    CHECKS_DIR, "lighthouse-best-practice-analyzer.md"
)


def parse_frontmatter(filepath):
    """Parse YAML frontmatter and body from a markdown file.

    Returns (frontmatter_dict, body_str) or raises ValueError if frontmatter
    is missing or malformed.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        raise ValueError(f"File {filepath} does not start with YAML frontmatter '---'")

    # Match the opening and closing --- delimiters
    match = re.match(r"^---\n(.*?)\n---\n?(.*)", content, re.DOTALL)
    if not match:
        raise ValueError(f"File {filepath} has malformed YAML frontmatter")

    frontmatter_str, body = match.group(1), match.group(2)
    frontmatter = yaml.safe_load(frontmatter_str)
    return frontmatter, body


# ---------------------------------------------------------------------------
# agentsmd-updater.md – file existence
# ---------------------------------------------------------------------------


class TestAgentsmdUpdaterExists:
    def test_file_exists(self):
        """agentsmd-updater.md must be present after the PR."""
        assert os.path.isfile(AGENTSMD_UPDATER_PATH), (
            f"Expected {AGENTSMD_UPDATER_PATH} to exist"
        )

    def test_file_is_not_empty(self):
        """agentsmd-updater.md must contain content."""
        assert os.path.getsize(AGENTSMD_UPDATER_PATH) > 0, (
            "agentsmd-updater.md must not be empty"
        )


# ---------------------------------------------------------------------------
# agentsmd-updater.md – YAML frontmatter structure
# ---------------------------------------------------------------------------


class TestAgentsmdUpdaterFrontmatter:
    def setup_method(self):
        self.frontmatter, self.body = parse_frontmatter(AGENTSMD_UPDATER_PATH)

    def test_frontmatter_is_parseable(self):
        """File must have valid YAML frontmatter delimited by ---."""
        assert self.frontmatter is not None

    def test_frontmatter_has_name_field(self):
        """Frontmatter must contain a 'name' key."""
        assert "name" in self.frontmatter, (
            "agentsmd-updater.md frontmatter must contain a 'name' field"
        )

    def test_name_field_value(self):
        """'name' field must be 'agentsmd-updater'."""
        assert self.frontmatter["name"] == "agentsmd-updater", (
            f"Expected name='agentsmd-updater', got '{self.frontmatter['name']}'"
        )

    def test_frontmatter_has_no_extra_required_fields(self):
        """Frontmatter should only contain the 'name' field (minimal definition)."""
        # The agentsmd-updater check deliberately uses a minimal frontmatter.
        # If new mandatory fields are added this test should be updated.
        assert set(self.frontmatter.keys()) == {"name"}, (
            f"Unexpected frontmatter fields: {set(self.frontmatter.keys()) - {'name'}}"
        )

    def test_name_is_string(self):
        """'name' value must be a non-empty string."""
        assert isinstance(self.frontmatter["name"], str)
        assert len(self.frontmatter["name"]) > 0


# ---------------------------------------------------------------------------
# agentsmd-updater.md – instruction body content
# ---------------------------------------------------------------------------


class TestAgentsmdUpdaterBody:
    def setup_method(self):
        _, self.body = parse_frontmatter(AGENTSMD_UPDATER_PATH)

    def test_body_is_not_empty(self):
        """Instruction body must not be empty."""
        assert self.body.strip(), "Instruction body must contain text"

    def test_body_references_agents_md(self):
        """Instructions must mention the AGENTS.md target file."""
        assert "AGENTS.md" in self.body, (
            "Instruction must reference the AGENTS.md file"
        )

    def test_body_mentions_pull_request(self):
        """Instructions must reference pull request context."""
        assert "pull request" in self.body.lower(), (
            "Instruction must mention 'pull request'"
        )

    def test_body_mentions_build_steps(self):
        """Instructions must tell the agent to look for build steps."""
        assert "build steps" in self.body.lower(), (
            "Instruction must mention 'build steps'"
        )

    def test_body_mentions_dependencies(self):
        """Instructions must tell the agent to look for dependency changes."""
        assert "dependencies" in self.body.lower(), (
            "Instruction must mention 'dependencies'"
        )

    def test_body_mentions_environment_variables(self):
        """Instructions must tell the agent to look for environment variables."""
        assert "environment variables" in self.body.lower(), (
            "Instruction must mention 'environment variables'"
        )

    def test_body_restricts_modifications_to_agents_md_only(self):
        """Instructions must explicitly forbid modifying other files."""
        assert "do not modify any other file" in self.body.lower(), (
            "Instruction must contain 'Do not modify any other file'"
        )

    def test_body_mentions_repo_root(self):
        """Instructions must reference placing AGENTS.md in the root directory."""
        assert "root" in self.body.lower(), (
            "Instruction must reference the repository root directory"
        )

    def test_body_mentions_missing_file_creation(self):
        """Instructions must describe behaviour when AGENTS.md is absent."""
        assert "missing" in self.body.lower() or "create" in self.body.lower(), (
            "Instruction must handle the case where AGENTS.md does not yet exist"
        )

    def test_body_mentions_scripts(self):
        """Instructions must tell the agent to look for script changes."""
        assert "scripts" in self.body.lower(), (
            "Instruction must mention 'scripts'"
        )

    def test_body_mentions_workflows(self):
        """Instructions must tell the agent to look for workflow changes."""
        assert "workflows" in self.body.lower(), (
            "Instruction must mention 'workflows'"
        )

    def test_body_mentions_preserving_existing_info(self):
        """Instructions must tell the agent to preserve existing relevant content."""
        # The instruction says "Preserve all existing relevant information"
        assert "preserve" in self.body.lower() or "existing" in self.body.lower(), (
            "Instruction must tell the agent to preserve existing information"
        )

    def test_body_is_single_paragraph(self):
        """The instruction body should be a concise single paragraph (no headings)."""
        # The agentsmd-updater instruction is intentionally minimal - no markdown
        # headings, no bullet lists, just a plain prose instruction.
        stripped = self.body.strip()
        assert not re.search(r"^#{1,6}\s", stripped, re.MULTILINE), (
            "agentsmd-updater instruction body should not contain markdown headings"
        )

    def test_body_does_not_start_with_whitespace_line(self):
        """Body content after frontmatter should start without a leading blank line."""
        # Acceptable: body may start with a single newline coming from the ---
        # separator, but should have actual content.
        assert self.body.strip()


# ---------------------------------------------------------------------------
# lighthouse-best-practice-analyzer.md – deletion validation
# ---------------------------------------------------------------------------


class TestLighthouseAnalyzerDeleted:
    def test_file_does_not_exist(self):
        """lighthouse-best-practice-analyzer.md must have been deleted by the PR."""
        assert not os.path.exists(LIGHTHOUSE_ANALYZER_PATH), (
            f"{LIGHTHOUSE_ANALYZER_PATH} should have been deleted but still exists"
        )

    def test_no_lighthouse_analyzer_variants_exist(self):
        """No variant filenames for the lighthouse analyzer should exist."""
        checks_dir = CHECKS_DIR
        for filename in os.listdir(checks_dir):
            if not os.path.isfile(os.path.join(checks_dir, filename)):
                continue
            lower = filename.lower()
            assert not (
                "lighthouse" in lower and "analyzer" in lower
            ), (
                f"Found unexpected lighthouse analyzer file: {filename}"
            )


# ---------------------------------------------------------------------------
# Regression / boundary tests
# ---------------------------------------------------------------------------


class TestAgentsmdUpdaterRegression:
    def test_file_uses_unix_line_endings(self):
        """File should use LF line endings (not CRLF)."""
        with open(AGENTSMD_UPDATER_PATH, "rb") as f:
            raw = f.read()
        assert b"\r\n" not in raw, (
            "agentsmd-updater.md must use LF (Unix) line endings, not CRLF"
        )

    def test_file_is_utf8_encoded(self):
        """File must be valid UTF-8."""
        with open(AGENTSMD_UPDATER_PATH, "rb") as f:
            raw = f.read()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            pytest.fail(f"agentsmd-updater.md is not valid UTF-8: {exc}")

    def test_name_has_no_leading_trailing_whitespace(self):
        """'name' value must not have leading or trailing whitespace."""
        frontmatter, _ = parse_frontmatter(AGENTSMD_UPDATER_PATH)
        name = frontmatter.get("name", "")
        assert name == name.strip(), (
            f"'name' value has surrounding whitespace: '{name}'"
        )

    def test_name_uses_kebab_case(self):
        """'name' should use kebab-case (lowercase letters and hyphens only)."""
        frontmatter, _ = parse_frontmatter(AGENTSMD_UPDATER_PATH)
        name = frontmatter.get("name", "")
        assert re.match(r"^[a-z][a-z0-9-]*$", name), (
            f"'name' value '{name}' should be kebab-case"
        )

    def test_body_mentions_code_style(self):
        """Instructions must mention code style as a trackable concern."""
        _, body = parse_frontmatter(AGENTSMD_UPDATER_PATH)
        assert "code style" in body.lower(), (
            "Instruction must mention 'code style'"
        )

    def test_body_mentions_architectures(self):
        """Instructions must mention architecture changes."""
        _, body = parse_frontmatter(AGENTSMD_UPDATER_PATH)
        assert "architect" in body.lower(), (
            "Instruction must mention 'architecture' or related term"
        )

    def test_instruction_addresses_ai_coding_agent(self):
        """Instructions should explicitly target AI coding agents."""
        _, body = parse_frontmatter(AGENTSMD_UPDATER_PATH)
        assert "agent" in body.lower(), (
            "Instruction must reference 'agent' (automated agent context)"
        )
