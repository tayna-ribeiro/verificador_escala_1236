"""
Testes de Integridade — Estrutura, Configuração e Ambiente
============================================================
Verifica se o projeto está "saudável" antes de subir para produção:
  - Arquivos obrigatórios existem
  - requirements.txt está completo
  - .env.example cobre as variáveis esperadas
  - Código importa sem erro com BOT_TOKEN mockado
  - Módulos não têm importações quebradas
"""

import os
import ast
import importlib
import sys
import pytest
from pathlib import Path


# Raiz do projeto (um nível acima deste arquivo)
PROJECT_ROOT = Path(__file__).parent.parent


# ------------------------------------------------------------------
# Testes de integridade de arquivos
# ------------------------------------------------------------------

class TestArquivosObrigatorios:
    """Garante que arquivos essenciais existem no repositório."""

    def test_bot_py_existe(self):
        assert (PROJECT_ROOT / "bot.py").is_file(), "bot.py não encontrado!"

    def test_flask_app_py_existe(self):
        assert (PROJECT_ROOT / "flask_app.py").is_file(), "flask_app.py não encontrado!"

    def test_requirements_txt_existe(self):
        assert (PROJECT_ROOT / "requirements.txt").is_file(), "requirements.txt não encontrado!"

    def test_env_example_existe(self):
        assert (PROJECT_ROOT / ".env.example").is_file(), (
            ".env.example não encontrado! Inclua um modelo das variáveis necessárias."
        )

    def test_gitignore_existe(self):
        assert (PROJECT_ROOT / ".gitignore").is_file(), ".gitignore não encontrado!"

    def test_readme_existe(self):
        assert (PROJECT_ROOT / "README.md").is_file(), "README.md não encontrado!"


# ------------------------------------------------------------------
# Testes de integridade do requirements.txt
# ------------------------------------------------------------------

class TestRequirements:
    """Verifica se as dependências críticas estão declaradas."""

    DEPENDENCIAS_OBRIGATORIAS = [
        "python-telegram-bot",
        "python-dotenv",
        "Flask",
    ]

    def _ler_requirements(self) -> str:
        return (PROJECT_ROOT / "requirements.txt").read_text(encoding="utf-8").lower()

    @pytest.mark.parametrize("pacote", DEPENDENCIAS_OBRIGATORIAS)
    def test_dependencia_declarada(self, pacote):
        conteudo = self._ler_requirements()
        assert pacote.lower() in conteudo, (
            f"Dependência '{pacote}' não encontrada no requirements.txt!"
        )

    def test_sem_linhas_em_branco_excessivas(self):
        """Não deve ter mais de 1 linha em branco consecutiva."""
        linhas = (PROJECT_ROOT / "requirements.txt").read_text().splitlines()
        em_branco_consecutivas = sum(
            1 for i in range(len(linhas) - 1)
            if linhas[i].strip() == "" and linhas[i + 1].strip() == ""
        )
        assert em_branco_consecutivas == 0, "requirements.txt tem linhas em branco desnecessárias."


# ------------------------------------------------------------------
# Testes de integridade do .env.example
# ------------------------------------------------------------------

class TestEnvExample:
    """Verifica se o .env.example documenta as variáveis necessárias."""

    VARIAVEIS_ESPERADAS = ["BOT_TOKEN", "WEBHOOK_SECRET"]

    def _ler_env_example(self) -> str:
        return (PROJECT_ROOT / ".env.example").read_text(encoding="utf-8")

    @pytest.mark.parametrize("variavel", VARIAVEIS_ESPERADAS)
    def test_variavel_documentada(self, variavel):
        conteudo = self._ler_env_example()
        assert variavel in conteudo, (
            f"Variável '{variavel}' não está documentada no .env.example!"
        )


# ------------------------------------------------------------------
# Testes de sintaxe do código-fonte
# ------------------------------------------------------------------

class TestSintaxePython:
    """Verifica se os arquivos .py não têm erros de sintaxe."""

    ARQUIVOS_PARA_CHECAR = [
        "bot.py",
        "flask_app.py",
        "configurar_webhook.py",
        "check_webhook.py",
        "remove_webhook.py",
    ]

    @pytest.mark.parametrize("arquivo", ARQUIVOS_PARA_CHECAR)
    def test_sem_erro_de_sintaxe(self, arquivo):
        caminho = PROJECT_ROOT / arquivo
        if not caminho.is_file():
            pytest.skip(f"{arquivo} não encontrado, pulando.")

        codigo = caminho.read_text(encoding="utf-8")
        try:
            ast.parse(codigo)
        except SyntaxError as e:
            pytest.fail(f"Erro de sintaxe em {arquivo}: {e}")


# ------------------------------------------------------------------
# Testes de importação dos módulos principais
# ------------------------------------------------------------------

class TestImportacoes:
    """Garante que os módulos importam corretamente com ambiente mockado."""

    def test_bot_importa_com_token_mockado(self, monkeypatch):
        """bot.py deve importar sem erro quando BOT_TOKEN está definido."""
        monkeypatch.setenv("BOT_TOKEN", "123456:FAKE_TOKEN_PARA_TESTE")
        monkeypatch.setenv("WEBHOOK_SECRET", "fake_secret")

        # Remove do cache para forçar reimportação limpa
        for mod in list(sys.modules.keys()):
            if mod.startswith("bot"):
                del sys.modules[mod]

        try:
            import bot  # noqa: F401
        except Exception as e:
            pytest.fail(f"bot.py falhou ao importar: {e}")

    def test_calculadora_exportada(self, monkeypatch):
        """CalculadoraEscala deve ser acessível via bot.py."""
        monkeypatch.setenv("BOT_TOKEN", "123456:FAKE_TOKEN_PARA_TESTE")

        from bot import CalculadoraEscala
        assert CalculadoraEscala is not None

    def test_estados_conversa_exportados(self, monkeypatch):
        """As constantes DATA_BASE e DATA_CONSULTA devem existir no módulo."""
        monkeypatch.setenv("BOT_TOKEN", "123456:FAKE_TOKEN_PARA_TESTE")

        from bot import DATA_BASE, DATA_CONSULTA
        assert isinstance(DATA_BASE, int)
        assert isinstance(DATA_CONSULTA, int)
        assert DATA_BASE != DATA_CONSULTA


# ------------------------------------------------------------------
# Testes de integridade do .gitignore
# ------------------------------------------------------------------

class TestGitignore:
    """Verifica se arquivos sensíveis estão no .gitignore."""

    ENTRADAS_ESPERADAS = [".env", "__pycache__", "*.pyc"]

    def _ler_gitignore(self) -> str:
        return (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")

    @pytest.mark.parametrize("entrada", ENTRADAS_ESPERADAS)
    def test_entrada_no_gitignore(self, entrada):
        conteudo = self._ler_gitignore()
        assert entrada in conteudo, (
            f"'{entrada}' não encontrado no .gitignore — risco de vazar arquivos sensíveis!"
        )
