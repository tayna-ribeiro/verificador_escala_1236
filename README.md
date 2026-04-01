# 🤖 Bot de Escala 12x36

Bot para Telegram que ajuda profissionais com escala 12x36 a saberem rapidamente se vão trabalhar ou folgar em qualquer data.

## ✨ Funcionalidades

- Saudação personalizada com nome do usuário
- Botão interativo direto no `/start`
- Verificação de qualquer data futura ou passada
- Validação estrita do formato de data (`DD/MM/AAAA`)
- Reinício automático do fluxo ao mandar qualquer mensagem

## 🚀 Como usar no Telegram

1. Inicie o bot com `/start`
2. Clique no botão **🔍 Verificar Minha Escala** ou envie `/verificar`
3. Informe a data do seu **último dia de trabalho** (plantão de referência)
4. Informe a **data que deseja consultar**
5. O bot responde se você estará de **Trabalho 🏢** ou **Folga 🏖️**

> Você também pode simplesmente mandar qualquer mensagem para reiniciar a verificação a qualquer momento.

## 🛠️ Como rodar localmente

### Pré-requisitos

- Python 3.10+
- Conta no Telegram e um bot criado via [@BotFather](https://t.me/BotFather)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio

# Instale as dependências
pip install python-telegram-bot python-dotenv
```

### Configuração

```bash
# Copie o arquivo de exemplo e preencha com seu token
cp .env.example .env
```

Edite o arquivo `.env`:
```
BOT_TOKEN=seu_token_do_botfather_aqui
```

### Executando

```bash
python bot.py
```

## 📁 Estrutura do Projeto

```
.
├── bot.py           # Código principal do bot
├── .env             # Variáveis de ambiente (não sobe para o GitHub!)
├── .env.example     # Modelo das variáveis de ambiente
├── .gitignore       # Arquivos ignorados pelo Git
└── README.md        # Este arquivo
```

## ⚙️ Variáveis de Ambiente

| Variável    | Descrição                              |
|-------------|----------------------------------------|
| `BOT_TOKEN` | Token do bot gerado pelo @BotFather    |

## 📜 Licença

Este projeto é de uso livre. Sinta-se à vontade para adaptar para sua escala!
