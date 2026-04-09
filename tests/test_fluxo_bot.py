"""
Testes de Integração — Fluxo da Conversa do Bot (ConversationHandler)
========================================================================
Simula mensagens do Telegram sem precisar de token real.
Usa `unittest.mock` para isolar a biblioteca python-telegram-bot.

Fluxo testado:
  /verificar  →  recebe data base  →  recebe data consulta  →  resultado
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from bot import (
    iniciar_verificacao,
    receber_data_base,
    receber_data_consulta,
    cancelar,
    _validar_data,
    DATA_BASE,
    DATA_CONSULTA,
)
from telegram.ext import ConversationHandler


# ------------------------------------------------------------------
# Helpers para criar mocks realistas do Telegram
# ------------------------------------------------------------------

def make_update(text: str = None, callback_data: str = None) -> MagicMock:
    """Cria um Update falso com mensagem de texto ou callback_query."""
    update = MagicMock()

    # Mensagem de texto
    update.message = MagicMock()
    update.message.text = text
    update.message.reply_text = AsyncMock()

    # Callback de botão (inline keyboard)
    update.callback_query = MagicMock() if callback_data else None
    if callback_data:
        update.callback_query.data = callback_data
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()

    return update


def make_context(user_data: dict = None) -> MagicMock:
    """Cria um Context falso com user_data controlado."""
    context = MagicMock()
    context.user_data = user_data or {}
    return context


# ------------------------------------------------------------------
# Testes: validação isolada (_validar_data)
# ------------------------------------------------------------------

class TestValidarData:
    """Testa o helper de validação de formato de data."""

    def test_formato_correto(self):
        assert _validar_data("01/04/2026") is True

    def test_formato_iso_invalido(self):
        assert _validar_data("2026-04-01") is False

    def test_texto_livre_invalido(self):
        assert _validar_data("hoje") is False

    def test_string_vazia_invalida(self):
        assert _validar_data("") is False

    def test_data_imposssivel_invalida(self):
        assert _validar_data("31/02/2026") is False

    def test_com_espacos_invalido(self):
        assert _validar_data(" 01/04/2026 ") is False  # sem strip aqui


# ------------------------------------------------------------------
# Testes: iniciar_verificacao (entry point do fluxo)
# ------------------------------------------------------------------

class TestIniciarVerificacao:
    """Testa a função que abre o fluxo de conversa."""

    @pytest.mark.asyncio
    async def test_via_texto_envia_mensagem(self):
        """Quando chamado via texto, deve responder e retornar DATA_BASE."""
        update = make_update(text="/verificar")
        context = make_context()

        resultado = await iniciar_verificacao(update, context)

        update.message.reply_text.assert_called_once()
        assert resultado == DATA_BASE

    @pytest.mark.asyncio
    async def test_via_callback_query_responde(self):
        """Quando chamado via botão inline, deve editar a mensagem e retornar DATA_BASE."""
        update = make_update(callback_data="verificar")
        context = make_context()

        resultado = await iniciar_verificacao(update, context)

        update.callback_query.answer.assert_called_once()
        update.callback_query.edit_message_text.assert_called_once()
        assert resultado == DATA_BASE


# ------------------------------------------------------------------
# Testes: receber_data_base
# ------------------------------------------------------------------

class TestReceberDataBase:
    """Testa o handler que recebe a data base do plantão."""

    @pytest.mark.asyncio
    async def test_data_valida_salva_e_avanca(self):
        """Data válida deve ser salva no contexto e avançar para DATA_CONSULTA."""
        update = make_update(text="01/04/2026")
        context = make_context()

        resultado = await receber_data_base(update, context)

        assert context.user_data.get("data_base") == "01/04/2026"
        assert resultado == DATA_CONSULTA

    @pytest.mark.asyncio
    async def test_data_invalida_permanece_no_estado(self):
        """Formato inválido deve manter o estado em DATA_BASE."""
        update = make_update(text="01-04-2026")
        context = make_context()

        resultado = await receber_data_base(update, context)

        assert resultado == DATA_BASE
        assert "data_base" not in context.user_data

    @pytest.mark.asyncio
    async def test_texto_livre_permanece_no_estado(self):
        """Texto qualquer deve manter o estado em DATA_BASE."""
        update = make_update(text="não sei")
        context = make_context()

        resultado = await receber_data_base(update, context)

        assert resultado == DATA_BASE


# ------------------------------------------------------------------
# Testes: receber_data_consulta
# ------------------------------------------------------------------

class TestReceberDataConsulta:
    """Testa o handler que recebe a data a ser consultada."""

    @pytest.mark.asyncio
    async def test_data_valida_retorna_resultado(self):
        """Data válida deve gerar resultado e encerrar a conversa."""
        update = make_update(text="03/04/2026")
        context = make_context(user_data={"data_base": "01/04/2026"})

        resultado = await receber_data_consulta(update, context)

        update.message.reply_text.assert_called_once()
        assert resultado == ConversationHandler.END

    @pytest.mark.asyncio
    async def test_resultado_contem_trabalha_ou_folga(self):
        """A resposta deve conter 'Trabalha' ou 'Folga'."""
        update = make_update(text="03/04/2026")
        context = make_context(user_data={"data_base": "01/04/2026"})

        await receber_data_consulta(update, context)

        chamada = update.message.reply_text.call_args
        texto_enviado = chamada[0][0] if chamada[0] else str(chamada)
        assert "Trabalha" in texto_enviado or "Folga" in texto_enviado

    @pytest.mark.asyncio
    async def test_data_invalida_permanece_em_data_consulta(self):
        """Formato inválido deve manter o estado em DATA_CONSULTA."""
        update = make_update(text="amanhã")
        context = make_context(user_data={"data_base": "01/04/2026"})

        resultado = await receber_data_consulta(update, context)

        assert resultado == DATA_CONSULTA

    @pytest.mark.asyncio
    async def test_cancelar_encerra_conversa(self):
        """O comando /cancelar deve encerrar a conversa."""
        update = make_update(text="/cancelar")
        context = make_context()

        resultado = await cancelar(update, context)

        update.message.reply_text.assert_called_once()
        assert resultado == ConversationHandler.END


# ------------------------------------------------------------------
# Testes: fluxo completo E2E (simulação ponta a ponta)
# ------------------------------------------------------------------

class TestFluxoCompletoE2E:
    """Simula o fluxo completo de uma conversa do início ao fim."""

    @pytest.mark.asyncio
    async def test_fluxo_completo_trabalha(self):
        """
        Fluxo:
          1. Usuário clica no botão => iniciar_verificacao
          2. Digita data base "01/04/2026"  => receber_data_base
          3. Digita data consulta "03/04/2026" => receber_data_consulta => Trabalha
        """
        context = make_context()

        # Passo 1 – botão
        update1 = make_update(callback_data="verificar")
        estado = await iniciar_verificacao(update1, context)
        assert estado == DATA_BASE

        # Passo 2 – data base
        update2 = make_update(text="01/04/2026")
        estado = await receber_data_base(update2, context)
        assert estado == DATA_CONSULTA
        assert context.user_data["data_base"] == "01/04/2026"

        # Passo 3 – data consulta (diferença de 2 dias => Trabalha)
        update3 = make_update(text="03/04/2026")
        estado = await receber_data_consulta(update3, context)
        assert estado == ConversationHandler.END

        chamada = update3.message.reply_text.call_args[0][0]
        assert "Trabalha" in chamada

    @pytest.mark.asyncio
    async def test_fluxo_completo_folga(self):
        """
        Fluxo completo com resultado Folga.
        Data base: 01/04/2026 | Consulta: 02/04/2026 => diferença 1 => Folga
        """
        context = make_context()

        update1 = make_update(text="/verificar")
        await iniciar_verificacao(update1, context)

        update2 = make_update(text="01/04/2026")
        await receber_data_base(update2, context)

        update3 = make_update(text="02/04/2026")
        estado = await receber_data_consulta(update3, context)

        assert estado == ConversationHandler.END
        chamada = update3.message.reply_text.call_args[0][0]
        assert "Folga" in chamada

    @pytest.mark.asyncio
    async def test_fluxo_com_erro_e_reenvio(self):
        """
        Fluxo com erro na data base, seguido de correção.
        O bot deve pedir novamente sem avançar de estado.
        """
        context = make_context()

        # Inicia
        update1 = make_update(text="/verificar")
        await iniciar_verificacao(update1, context)

        # Data inválida
        update2 = make_update(text="data-errada")
        estado = await receber_data_base(update2, context)
        assert estado == DATA_BASE  # Não avançou

        # Data correta
        update3 = make_update(text="01/04/2026")
        estado = await receber_data_base(update3, context)
        assert estado == DATA_CONSULTA  # Agora avançou
