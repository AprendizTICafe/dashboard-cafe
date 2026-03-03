# ☕ Painel Café do Sítio - Sistema de Gestão de Advertências

O **Sistema de Gestão de Advertências** é uma aplicação web corporativa de missão crítica desenvolvida para digitalizar e padronizar o ciclo disciplinar da Café do Sítio. A ferramenta automatiza o fluxo desde a solicitação inicial até a formalização pelo RH, garantindo conformidade jurídica e agilidade na comunicação.

## 🚀 Funcionalidades

* **Ciclo Disciplinar Completo:** Gestão de advertências, suspensões e suporte a processos de sindicância.
* **Workflow de Aprovação:** Fluxo inteligente que integra Gestores, Diretoria e Recursos Humanos.
* **Autenticação Enterprise:** Login seguro integrado ao **Microsoft 365 (Azure Active Directory)** via **OAuth 2.0**.
* **Notificações Automáticas:** Envio de alertas em tempo real via **WhatsApp (Z-API)** a cada mudança de status no processo.
* **Banco de Dados Centralizado:** Histórico completo de ocorrências para consulta e auditoria.

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia |
| :--- | :--- |
| **Linguagem** | Python |
| **Interface** | HTML5 / CSS3 |
| **Banco de Dados** | MySQL |
| **Autenticação** | Microsoft Azure AD (OAuth2.0) |
| **Comunicação** | Z-API (WhatsApp API) |

## 📐 Arquitetura do Processo

O sistema foi desenhado para seguir a hierarquia e os protocolos de conformidade da empresa:

1.  **Abertura:** O gestor solicita a medida disciplinar via formulário web.
2.  **Revisão de Diretoria:** Análise estratégica e aprovação da solicitação.
3.  **Sindicância (se aplicável):** Módulo para investigação e coleta de evidências.
4.  **Formalização RH:** Geração da documentação e encerramento do processo.
5.  **Notificações:** Durante todo o percurso, os envolvidos recebem atualizações automáticas via WhatsApp.

## ⚙️ Configuração do Ambiente

### Pré-requisitos
* Python 3.8+
* Servidor MySQL
* Conta no Azure Portal (App Registration para OAuth2)
* Token ativo na Z-API
