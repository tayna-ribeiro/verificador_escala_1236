# 🤖 Bot de Escala 12x36

[![CI — Verificador de Escala](https://github.com/seu-usuario/verificaEscala1236/actions/workflows/ci.yml/badge.svg)](https://github.com/seu-usuario/verificaEscala1236/actions/workflows/ci.yml)

Bot para Telegram que ajuda profissionais com escala 12x36 a saberem rapidamente se vão trabalhar ou folgar em qualquer data.

## ✨ Funcionalidades

- Saudação personalizada com o nome do usuário
- Botão interativo direto no `/start`
- Verificação de qualquer data futura ou passada
- Validação estrita do formato de data (`DD/MM/AAAA`)
- Fluxo de conversa guiado passo a passo
- Tratamento de mensagens fora do fluxo com orientação ao usuário

## 🚀 Como usar no Telegram

1. Inicie o bot com `/start`
2. Clique no botão **🔍 Verificar Minha Escala** ou envie `/verificar`
3. Informe a data do seu **último dia de trabalho** (plantão de referência)
4. Informe a **data que deseja consultar**
5. O bot responde se você estará de **Trabalho 🏢** ou **Folga 🏖️**

> Para cancelar a qualquer momento, envie `/cancelar`.

---

## 🛠️ Como rodar localmente

### Pré-requisitos

- Python 3.10 ou superior
- Conta no Telegram e um bot criado via [@BotFather](https://t.me/BotFather)

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/verificaEscala1236.git
cd verificaEscala1236
```

### 2. Crie e ative o ambiente virtual

> ⚠️ **Importante:** em sistemas Linux/Ubuntu modernos (Debian 12+), instalar pacotes Python diretamente com `pip` causa um erro de ambiente gerenciado externamente. Sempre use um ambiente virtual.

```bash
# Criar o ambiente virtual (só precisa fazer uma vez)
python3 -m venv .venv

# Ativar (Linux/macOS)
source .venv/bin/activate

# Ativar (Windows)
.venv\Scripts\activate
```

Após ativar, o terminal mostrará `(.venv)` no início da linha.

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
# Copie o arquivo de modelo
cp .env.example .env
```

Edite o arquivo `.env` com seus dados reais:

```env
BOT_TOKEN=seu_token_do_botfather_aqui
WEBHOOK_SECRET=uma_string_aleatoria_segura
```

> 💡 Para gerar um `WEBHOOK_SECRET` seguro:
> ```bash
> python3 -c "import secrets; print(secrets.token_hex(32))"
> ```

### 5. Execute o bot

```bash
python bot.py
```

### 6. Desativar o ambiente virtual (quando terminar)

```bash
deactivate
```

---

## 🧪 Testes Automatizados

O projeto conta com uma suíte completa de testes dividida em três categorias:

| Arquivo | Tipo | O que verifica |
|---|---|---|
| `tests/test_calculadora.py` | **Unitários** | Lógica de cálculo da escala 12x36 |
| `tests/test_fluxo_bot.py` | **Integração** | Fluxo completo da conversa (com mocks do Telegram) |
| `tests/test_integridade.py` | **Integridade** | Estrutura de arquivos, sintaxe, variáveis de ambiente |

### Rodando os testes

```bash
# Ativar o ambiente virtual antes
source .venv/bin/activate

# Todos os testes
pytest

# Apenas um arquivo específico
pytest tests/test_calculadora.py

# Com relatório de cobertura de código
pytest --cov=bot --cov-report=term-missing
```

---

## 🔄 Pipeline CI/CD (GitHub Actions)

A cada `push` ou `pull request` na branch `main`, o pipeline executa automaticamente:

```
push → Lint (flake8) → Testes (Python 3.10, 3.11, 3.12) → Integridade → ✅ Resumo
```

| Job | Descrição |
|---|---|
| 🔍 **Lint** | Verifica erros de sintaxe e estilo com `flake8` |
| 🧪 **Testes** | Roda a suíte completa em 3 versões do Python simultaneamente |
| 🛡️ **Integridade** | Valida estrutura, arquivos e configurações do projeto |
| ✅ **Status** | Consolida o resultado geral do pipeline |

> Os resultados ficam visíveis na aba **Actions** do repositório no GitHub.

---

## 📁 Estrutura do Projeto

```
verificaEscala1236/
├── .github/
│   └── workflows/
│       └── ci.yml            # Pipeline de CI/CD (GitHub Actions)
├── tests/
│   ├── __init__.py
│   ├── test_calculadora.py   # Testes unitários da lógica de escala
│   ├── test_fluxo_bot.py     # Testes de integração do fluxo de conversa
│   └── test_integridade.py   # Testes de integridade do projeto
├── .env                      # ⚠️ Variáveis reais — NÃO sobe para o GitHub!
├── .env.example              # Modelo das variáveis de ambiente
├── .gitignore                # Arquivos ignorados pelo Git
├── .venv/                    # ⚠️ Ambiente virtual — NÃO sobe para o GitHub!
├── bot.py                    # Código principal do bot (polling)
├── flask_app.py              # Servidor webhook (para deploy no PythonAnywhere)
├── pytest.ini                # Configuração central dos testes
├── requirements.txt          # Dependências do projeto
└── README.md                 # Este arquivo
```

---

## ⚙️ Variáveis de Ambiente

| Variável         | Descrição                                                        | Obrigatória |
|------------------|------------------------------------------------------------------|:-----------:|
| `BOT_TOKEN`      | Token do bot gerado pelo @BotFather                              | ✅ Sim      |
| `WEBHOOK_SECRET` | String secreta para autenticar requisições do webhook do Telegram | ✅ Sim      |

---

## 📜 Licença

Este projeto é de uso livre. Sinta-se à vontade para adaptar para sua escala!
