from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_client_neutral_mcp_installer_is_present_and_portable():
    installer = ROOT / "scripts" / "install-mcp.sh"
    text = installer.read_text()
    assert installer.stat().st_mode & 0o111
    assert "/home/hermes" not in text
    assert "mcpServers" in text
    assert '"command"' in text


def test_public_operations_doc_has_no_machine_specific_home_path():
    text = (ROOT / "OPERATIONS.md").read_text()
    assert "/home/hermes" not in text
    assert "freezetheworld/agent-search-stack" in text


def test_primary_readme_is_agent_neutral():
    text = (ROOT / "README.md").read_text()
    first_section = text.split("## Verify", 1)[0]
    assert text.startswith("# Agent Search Stack\n")
    assert "Hermes AgentSearch" not in text
    assert "hermes-agent-search" not in text
    assert "any AI agent" in first_section


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
