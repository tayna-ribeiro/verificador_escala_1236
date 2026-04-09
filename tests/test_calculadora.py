"""
Testes Unitários — CalculadoraEscala
=====================================
Verifica a lógica de cálculo de escala 12x36:
 - Diferença par  => Trabalha
 - Diferença ímpar => Folga
 - Mesma data      => Trabalha (diferença == 0)
 - Formato inválido de data na consulta
"""

import pytest
from bot import CalculadoraEscala


class TestCalculadoraEscala:
    """Testes da classe principal de cálculo de escala."""

    # ------------------------------------------------------------------
    # Testes de criação do objeto
    # ------------------------------------------------------------------

    def test_instanciacao_valida(self):
        """Deve criar a calculadora sem erro com data válida."""
        calc = CalculadoraEscala("01/04/2026")
        assert calc is not None

    def test_instanciacao_data_invalida(self):
        """Deve lançar ValueError ao receber formato de data errado."""
        with pytest.raises(ValueError):
            CalculadoraEscala("2026-04-01")  # formato ISO, não aceito

    def test_instanciacao_data_impossivel(self):
        """Deve lançar ValueError para datas impossíveis (ex.: 31/02)."""
        with pytest.raises(ValueError):
            CalculadoraEscala("31/02/2026")

    # ------------------------------------------------------------------
    # Testes de lógica de escala
    # ------------------------------------------------------------------

    def test_mesma_data_trabalha(self):
        """Diferença de 0 dias (par) => Trabalha."""
        calc = CalculadoraEscala("01/04/2026")
        resultado = calc.verificar_dia("01/04/2026")
        assert "Trabalha" in resultado

    def test_diferenca_par_trabalha(self):
        """Diferença de 2 dias (par) => Trabalha."""
        calc = CalculadoraEscala("01/04/2026")
        resultado = calc.verificar_dia("03/04/2026")
        assert "Trabalha" in resultado

    def test_diferenca_impar_folga(self):
        """Diferença de 1 dia (ímpar) => Folga."""
        calc = CalculadoraEscala("01/04/2026")
        resultado = calc.verificar_dia("02/04/2026")
        assert "Folga" in resultado

    def test_diferenca_impar_grande_folga(self):
        """Diferença de 3 dias (ímpar) => Folga."""
        calc = CalculadoraEscala("01/04/2026")
        resultado = calc.verificar_dia("04/04/2026")
        assert "Folga" in resultado

    def test_diferenca_par_grande_trabalha(self):
        """Diferença de 36 dias (par) => Trabalha."""
        calc = CalculadoraEscala("01/01/2026")
        resultado = calc.verificar_dia("06/02/2026")
        assert "Trabalha" in resultado

    def test_data_passada_trabalha(self):
        """Consulta em data anterior à base com diferença par => Trabalha."""
        calc = CalculadoraEscala("10/04/2026")
        resultado = calc.verificar_dia("08/04/2026")   # -2 dias, par
        assert "Trabalha" in resultado

    def test_data_passada_folga(self):
        """Consulta em data anterior à base com diferença ímpar => Folga."""
        calc = CalculadoraEscala("10/04/2026")
        resultado = calc.verificar_dia("09/04/2026")   # -1 dia, ímpar
        assert "Folga" in resultado

    def test_virada_de_mes(self):
        """Deve calcular corretamente ao cruzar virada de mês."""
        calc = CalculadoraEscala("28/04/2026")
        # 30/04 => diferença de 2 dias => Trabalha
        assert "Trabalha" in calc.verificar_dia("30/04/2026")
        # 01/05 => diferença de 3 dias => Folga
        assert "Folga" in calc.verificar_dia("01/05/2026")

    def test_virada_de_ano(self):
        """Deve calcular corretamente ao cruzar virada de ano."""
        calc = CalculadoraEscala("30/12/2025")
        # 01/01/2026 => diferença de 2 dias => Trabalha
        assert "Trabalha" in calc.verificar_dia("01/01/2026")
        # 31/12/2025 => diferença de 1 dia => Folga
        assert "Folga" in calc.verificar_dia("31/12/2025")

    # ------------------------------------------------------------------
    # Testes de validação do formato da data consultada
    # ------------------------------------------------------------------

    def test_formato_invalido_retorna_mensagem(self):
        """Deve retornar mensagem de erro elegante para formato errado."""
        calc = CalculadoraEscala("01/04/2026")
        resultado = calc.verificar_dia("01-04-2026")
        assert "inválido" in resultado.lower() or "Formato" in resultado

    def test_texto_puro_retorna_mensagem(self):
        """Texto aleatório não deve gerar exceção, apenas mensagem de erro."""
        calc = CalculadoraEscala("01/04/2026")
        resultado = calc.verificar_dia("amanhã")
        assert "inválido" in resultado.lower() or "Formato" in resultado

    def test_data_vazia_retorna_mensagem(self):
        """String vazia deve retornar mensagem de erro."""
        calc = CalculadoraEscala("01/04/2026")
        resultado = calc.verificar_dia("")
        assert "inválido" in resultado.lower() or "Formato" in resultado
