# SonarQube Automation

Esta pasta do projeto automatiza a análise de repositórios de código usando o SonarQube, rodando a ferramenta SonarQube Scanner para cada repositório e salvando os resultados utilizando a API REST do SonarQube.

---

## Estrutura de pastas

- `config/` → configurações do SonarQube (variáveis de ambiente, como URL e token)
- `core/` → código que executa o SonarQube Scanner para os repositórios e consulta a API para obter os resultados
- `data/repos/` → onde os repositórios a serem analisados devem ser armazenados
- `data/sonarqube/` → onde os resultados da análise do SonarQube são salvos
- `sonar_runner.py` → script principal que executa a análise dos repositórios

---

## Antes de rodar

1. Vá até o arquivo `config/.env`
2. Adicione as variáveis de ambiente:
    - `SONARQUBE_URL` → URL do seu servidor SonarQube (ex: `http://localhost:9000`)
    - `SONARQUBE_TOKEN` → Seu token de autenticação do SonarQube
3. Certifique-se de que o SonarQube está rodando. Você pode usar Docker para iniciar rapidamente:
    ```bash
    docker run -d -p 9000:9000 -v sonar_data:/opt/sonarqube/data -v sonar_extensions:/opt/sonarqube/extensions sonarqube
    ```

4. (Opcional) Se ainda não tiver, crie uma conta no SonarQube e gere um token de autenticação para usá-lo na variável `SONARQUBE_TOKEN`.

---

## Como rodar

1. Clone o repositório:

    ```bash
    git clone <url_do_repositório>
    cd <diretório_do_repositório>
    ```

2. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

3. Coloque os repositórios que você deseja analisar na pasta `data/repos/`.

4. Execute o script:

    ```bash
    python core/sonar_runner.py
    ```

   O script irá processar todos os repositórios na pasta `data/repos/`, rodar a análise com o SonarQube Scanner e salvar os resultados em `data/sonarqube/` no formato JSON.

---

## Solução de Problemas

- **Erro ao rodar o sonar-scanner**: Verifique se o SonarQube está rodando corretamente na URL configurada (http://localhost:9000).
- **Exportação em JSON não funciona**: A exportação direta de resultados em JSON pode não funcionar em versões mais recentes do SonarQube Scanner. Se isso acontecer, o script agora usa a **API REST** do SonarQube para buscar as issues após a análise e salva os resultados em arquivos JSON.

   Para mais detalhes sobre a API REST, consulte a [documentação do SonarQube](https://sonarqube.github.io).

---

## Estrutura de Pastas Detalhada

- `config/` → Contém o arquivo `.env` com as variáveis de ambiente.
- `core/` → Contém o código responsável por rodar o SonarQube Scanner nos repositórios e buscar as issues via API.
- `data/repos/` → Onde os repositórios a serem analisados devem ser armazenados.
- `data/sonarqube/` → Onde os resultados da análise serão salvos (em formato JSON).
- `sonar_runner.py` → O script que realiza a automação da análise com SonarQube.

---

Pronto! Após configurar tudo, o script irá analisar os repositórios configurados, buscar as issues via API e gerar os resultados automaticamente em formato JSON.
