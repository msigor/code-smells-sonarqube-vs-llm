
# Repo Miner

Esta pasta do projeto serve para clonar repositórios do GitHub de forma organizada.

---

## Estrutura de pastas

- `config/` → configurações gerais (lista de repositórios e token do GitHub)
- `core/` → código que faz a clonagem dos repositórios
- `data/raw_repos/` → onde os repositórios baixados são salvos
- `main.py` → script principal que executa a clonagem


---

## Antes de rodar

1. Vá até o arquivo `repo_miner/config/settings.py`
2. Adicione os repositórios na lista `REPOSITORIES`, depois haverá atualização para seleção automática com base nos critérios.
3. (Opcional) Se for clonar repositórios privados, adicione seu token do GitHub na variável `GITHUB_TOKEN`

---

Pronto! Depois disso, o script vai clonar os repositórios que você configurou.
