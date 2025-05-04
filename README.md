# Análise Comparativa entre LLMs com o uso de Engenharia de Prompt e o SonarQube na Detecção Automatizada de Code Smells em Projetos Java

Analisar e comparar abordagens automatizadas de detecção de code smells com o propósito de avaliar sua efetividade e confiabilidade, do ponto de vista de um pesquisador em engenharia de software, no contexto de projetos de software reais.

## Alunos integrantes da equipe

* Arthur Capanema Bretas
* Bernardo Cavanellas Biondini
* Gabriel Vitor de OLiveira Morais
* Igor Miranda Santos
* Júlia Borges Araújo Silva
* Letícia Rodrigues Blom de Paula

## Professores responsáveis

* Angélica Matos Guimarães Dias
* Jose Laerte Pires Xavier Junior
* Joana Gabriela Ribeiro de Souza

## Instruções de utilização

[Assim que a primeira versão do sistema estiver disponível, deverá complementar com as instruções de utilização. Descreva como instalar eventuais dependências e como executar a aplicação.]

O projeto consiste na mineiração de repositórios do GitHub e a análise estática do código por meio do Sonar Qube e uma LLM (Large Language Models)
comparando os resultados das análises para avaliar a efetividade e a confiabilidade das ferramentas.

### Versões

- **1.0**
    
    Na primeira versão executamos a clonagem de um repositório Java do GitHub e aplicamos a análise do repositório pelo Sonar e pela LLM escolhida.
    
    **Exigências:**
    
    - Python instalado
    - Cópia dos `.env.example` e preenchimento comas variáveis pessoais

    **Execução:**
    - Na raiz do projeto execute o comando `pip install requirements.txt` para instalar as dependências necessárias
    - Vá até a pasta "Codigo/repo_miner" `cd Codigo/repo_miner`
    - Execute o arquivo "main.py" `py main.py`
    - Após a clonagem do repositório execute o arquivo "main.py" da pasta "code_smell_study" `cd ../code_smell_study` `py main.py`
    - Após o término da execução os gráficos serão gerados e colocados na pasta "Codigo/code_smell_study/data/results"


    