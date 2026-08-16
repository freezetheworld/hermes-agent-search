from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_hermes_installer_is_present_and_portable():
    installer = ROOT / "scripts" / "install-hermes.sh"
    text = installer.read_text()
    assert installer.stat().st_mode & 0o111
    assert "/home/hermes" not in text
    assert "hermes mcp add" in text


def test_public_operations_doc_has_no_machine_specific_home_path():
    text = (ROOT / "HERMES-OPERATIONS.md").read_text()
    assert "/home/hermes" not in text
    assert "freezetheworld/hermes-agent-search" in text


def test_upstream_attribution_is_explicit():
    text = (ROOT / "UPSTREAM.md").read_text()
    assert "brcrusoe72/agent-search" in text
    assert "MIT License" in text


def test_skill_frontmatter_and_body_are_valid():
    text = (ROOT / "skills" / "web-research-stack" / "SKILL.md").read_text()
    assert text.startswith("---\n")
    assert "\nname: web-research-stack\n" in text
    assert "\ndescription:" in text
    assert "\n---\n\n# Web Research Stack" in text