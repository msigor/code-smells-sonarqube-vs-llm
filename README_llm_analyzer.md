# LLM Analyzer Automation

Este módulo automatiza a análise de code smells em repositórios de código-fonte utilizando a API da OpenAI. Ele divide os arquivos em pedaços analisáveis (chunks), envia cada chunk para um modelo GPT e salva os resultados em JSON.

---

## Estrutura de pastas

```
code_smell_study/
├── config/                # Configurações centrais e variáveis de ambiente
│   ├── .env               # OPENAI_API_KEY e OPENAI_MODEL
│   └── settings.py        # Paths, repositórios, extensões e prompt
├── core/                  # Lógica de chunking, chamadas à API e integração existente
│   ├── llm_analyzer.py    # Chunking e chamadas OpenAI
│   ├── sonar_runner.py    # Integração com SonarQube (existente)
│   └── report_generator.py# Geração de relatórios (existente)
├── data/
│   └── llm/               # Resultados JSON da análise LLM
└── main.py                # Script principal que orquestra todo o fluxo
```

---

## Antes de rodar

1. **Configurar variáveis de ambiente**:
   - Edite `config/.env` e adicione:
     ```env
     OPENAI_API_KEY=sk-...
     OPENAI_MODEL=gpt-3.5-turbo  # opcional (padrão: gpt-3.5-turbo)
     ```
2. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Preparar repositórios**:
   - Certifique-se de clonar ou copiar os repositórios em `repo_miner/data/raw_repos/`.
   - Ajuste `REPOSITORIES` e `MAX_REPOS` em `config/settings.py` conforme necessário.

---

## Como rodar

1. Ative o ambiente Python:
   ```bash
   source .venv/bin/activate  # Linux/macOS
   # ou
   .venv\Scripts\activate   # Windows
   ```
2. Execute o script principal:
   ```bash
   python main.py
   ```
3. O script irá:
   - Percorrer cada repositório em `repo_miner/data/raw_repos/`
   - Identificar arquivos com extensões definidas em `CODE_EXTENSIONS`
   - Dividir o código em chunks de até `MAX_TOKENS` tokens
   - Enviar cada chunk à API OpenAI (modelo definido em `OPENAI_MODEL`)
   - Salvar cada resposta em `data/llm/<repo_name>/<arquivo>_chunk<idx>.json`

---

## Solução de problemas

- **Retorno não é JSON válido**:
  - Ajuste o `SYSTEM_PROMPT` em `settings.py` para reforçar o formato estrito.
  - Verifique se há mensagens extras sendo retornadas pelo modelo.
  - Caso não consiga reporte o erro para o responsável da parte de prompt (Igor)

---

## Estrutura de pastas detalhada

- `config/` → Contém `.env` e `settings.py` com todas as configurações e prompts.
- `core/` → 
  - `llm_analyzer.py`: funções de `split_into_chunks()` e `analyze_with_llm()`.
  - `sonar_runner.py`: integração com SonarQube (análise tradicional).
  - `report_generator.py`: gera relatórios agregados.
- `data/llm/` → Resultados de cada análise chunk em JSON.
- `main.py` → Orquestra o processo completo de chunking, análise e persistência.

---

Pronto! Após configurar, basta rodar `python main.py` para obter análises de code smells automatizadas via LLM em JSON.
