## Documentação do Projeto

### Objetivo

Este projeto tem como objetivo comparar a eficácia da detecção de *code smells* (maus cheiros de código) em projetos Java utilizando duas abordagens distintas:

* **SonarQube**: uma ferramenta estática amplamente utilizada para análise de qualidade de código.
* **LLM (Large Language Model)**: modelo de linguagem natural usado para analisar e identificar *code smells* de forma automatizada.

---

### Ferramentas Utilizadas

| Ferramenta               | Descrição                                                                                         |
| ------------------------ | ------------------------------------------------------------------------------------------------- |
| **Python**               | Linguagem principal utilizada para orquestrar a execução dos scripts.                             |
| **SonarQube**            | Ferramenta de análise estática de código para detectar *code smells*, vulnerabilidades e bugs.    |
| **LLM API**              | Um modelo de linguagem (como o ChatGPT) acessado via API, utilizado para analisar o código fonte. |
| **Git**                  | Controle de versão e clonagem de repositórios do GitHub.                                          |
| **Matplotlib / Seaborn** | Bibliotecas Python utilizadas para geração de gráficos comparativos.                              |
| **dotenv**               | Biblioteca Python para leitura de variáveis de ambiente via arquivos `.env`.                      |

---

### Estrutura do Projeto

```
Codigo/
├── code_smell_study/     # Scripts para análise de code smells e geração de gráficos
│   ├── data/             # Resultados e gráficos gerados
│   └── core/             # Scripts de análise e comparação
│   └── main.py           # Script principal de análise e comparação
├── repo_miner/           # Scripts para clonagem e preparação dos repositórios
│   └── main.py           # Script para clonar e estruturar os projetos a serem analisados
requirements.txt          # Dependências do projeto
```

---

### Etapas de Execução

[Visualizar README](../README.md)

---

### 📊 Resultados Esperados

Após a execução, o projeto gerará comparações visuais entre os *code smells* detectados pelo SonarQube e pela LLM, permitindo analisar semelhanças, divergências e possíveis oportunidades de aprimoramento na detecção automatizada de *code smells* usando IA.