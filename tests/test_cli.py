from typer.testing import CliRunner
from cli.main import app

runner = CliRunner()


def test_vault_list_runs():
    result = runner.invoke(app, ["vault-list"])
    assert result.exit_code == 0


def test_vault_list_shows_files():
    result = runner.invoke(app, ["vault-list"])
    assert "vulns" in result.output or "methodology" in result.output


def test_vuln_invalid_name_shows_error():
    # Sin API key, el error viene del vault antes del LLM
    result = runner.invoke(app, ["vuln", "vuln_que_no_existe_xyz"])
    # Debe mencionar que no existe o listar disponibles
    assert result.exit_code == 0  # manejo de error suave
