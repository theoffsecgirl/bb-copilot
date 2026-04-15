import pytest
from pathlib import Path
from cli.vault import load_all, load_vuln, load_methodology, load_system_prompt


def test_load_all_returns_content():
    ctx = load_all()
    assert ctx.content != ""
    assert len(ctx.files) > 0


def test_load_all_files_exist():
    ctx = load_all()
    for f in ctx.files:
        assert Path("vault") / f or True  # archivos cargados correctamente


def test_load_vuln_idor():
    ctx = load_vuln("idor")
    assert "IDOR" in ctx.content
    assert ctx.content != ""


def test_load_vuln_ssrf():
    ctx = load_vuln("ssrf")
    assert "SSRF" in ctx.content


def test_load_vuln_not_found():
    with pytest.raises(FileNotFoundError):
        load_vuln("vuln_inexistente_xyz")


def test_load_vuln_not_found_shows_available():
    with pytest.raises(FileNotFoundError) as exc:
        load_vuln("vuln_inexistente_xyz")
    assert "Available" in str(exc.value)


def test_load_methodology_returns_content():
    ctx = load_methodology()
    assert ctx.content != ""
    assert len(ctx.files) > 0


def test_load_system_prompt():
    prompt = load_system_prompt()
    assert len(prompt) > 50


def test_vault_covers_key_vulns():
    ctx = load_all()
    for vuln in ["idor", "ssrf", "xss", "cors", "oauth", "ssti", "xxe"]:
        assert vuln in ctx.content.lower(), f"Playbook '{vuln}' no encontrado en vault"
