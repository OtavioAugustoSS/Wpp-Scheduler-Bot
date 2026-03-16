# 🧠 Assistente Virtual Inteligente para WhatsApp (Arrodes AI)

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)
![NVIDIA_NIM](https://img.shields.io/badge/Llama_3.1-NVIDIA_NIM-76B900.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

Um agente de inteligência artificial proativo, projetado para operar totalmente via WhatsApp. Muito além de um simples chatbot de regras rígidas, o Arrodes AI utiliza **Processamento de Linguagem Natural Avançado (LLM Llama 3.1)** para bater papo, interpretar necessidades e estruturar agendas complexas de forma assíncrona.

Este bot permite que o usuário gerencie sua rotina através de uma conversa fluida: desde o agendamento de tarefas pontuais até compromissos recorrentes com padrões Cron, tudo validado por inteligência artificial e persistido em banco de dados.

## ✨ Principais Funcionalidades

- **🎙️ Conversação Natural Inteligente**: Entende áudio/texto e possui contexto dinâmico da vida do usuário, focado na produtividade, estudos (como Engenharia de Software) e gestão de tempo.
- **📅 Agendamento Inteligente**: Capacidade de diferenciar agendamentos de *Evento Único* (`schedule_once`) e rotinas *Recorrentes* (`schedule_recurring`) com base nas mensagens do usuário sem necessidade de comandos fixos (ex: "Me lembre de beber água toda hora" -> `0 * * * *`).
- **🧠 Injeção de Contexto e Memória de Curto Prazo**:
  - O bot mantém o fio da meada salvando as últimas mensagens na sua memória.
  - Ele lê proativamente o banco de dados antes de cada interação, permitindo que responda imediatamente a perguntas casuais como "Qual é a minha rotina amanhã?".
- **🛡️ Tolerância à Falhas (Smart Fallback Parser)**: Mecanismos RegEx implementados para garantir que quebras inesperadas do LLM (Markdown extra, "alucinações" de texto puro) não crashem o sistema, embrulhando textos em estruturas JSON válidas em tempo real.
- **⏰ Motor Cron/Scheduler (APScheduler)**: Roda assincronamente em segundo plano varrendo e despachando lembretes proativos diretamente pelo WhatsApp.
- **☁️ Pronta para Deploy**: Containerizada (Dockerfile) e pronta para rodar em nuvem de hospedagem (Render, Railway, Heroku, VPS).

---

## 🛠️ Stack Tecnológica (Habilidades Utilizadas)

- **Back-End API**: Python, FastAPI
- **Inteligência Artificial (LLM)**: LLama 3.1-70B via Integração de API NVIDIA NIM (OpenAI Python Client compatível).
- **Banco de Dados (ORM)**: SQLAlchemy 2.0 com modelo Async (aiosqlite) - facilmente migrável para PostgreSQL.
- **Jobs e Tasks Assíncronos**: APScheduler integrado diretamente ao loop do Uvicorn.
- **Arquitetura de Softwares / Integrações**: Webhooks seguros da Meta Cloud API (WhatsApp Business).
- **Infraestrutura**: Docker.

---

## 🚀 Como Executar Localmente

### 1. Pré-Requisitos
- Python 3.11+
- Conta de desenvolvedor Meta: [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api) configurada para enviar/receber webhooks.
- Chave de API da NVIDIA NIM.

### 2. Instalação e Configuração

Clone o repositório e instale as dependências:
```bash
git clone https://github.com/SeuUsuario/Wpp-Scheduler-Bot.git
cd Wpp-Scheduler-Bot
pip install -r requirements.txt
```

### 3. Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto baseado no `.env.example`:
```env
NVIDIA_API_KEY=sua_chave_nvidia
WHATSAPP_VERIFY_TOKEN=token_seguro_da_sua_escolha_para_webhook
WHATSAPP_API_TOKEN=Bearer_token_da_meta
WHATSAPP_PHONE_ID=id_do_numero_do_seu_telefone_de_testes
```

### 4. Rodando a Aplicação
Suba o servidor e expose sua porta em algum serviço de túnel local (Ngrok) ou faça push no Render / Railway.
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
---

## ☁️ Deploy para o Render (Nuvem)

A aplicação foi montada com um empacotamento em `Dockerfile` leve (`python:3.11-slim`), focada em otimização de caching do Docker.

1. Faça push do seu código para uma branch no GitHub.
2. Acesse a Dashboard do **Render**, crie um **New Web Service**.
3. Selecione a opção **Docker Build** e deixe o Render puxar do seu branch.
4. Cadastre suas mesmas propriedades do `.env` na aba de *Environment Variables* do painel.
5. Inicie sua aplicação de pé e atualize as URLs do Meta Developer Console para espelhar para seu domínio gerado pelo Render `https://seu-nome.render.com/webhook`.

---
*Este projeto foi inteiramente desenhado e guiado pelas melhores práticas do modelo limpo de desenvolvimento de software assíncrono moderno para Chatbots Humanizados de Alta Resposta e Gestão Preditiva.*