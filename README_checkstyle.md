# Análise de Code Smells com CheckStyle

Este documento detalha como usar o módulo CheckStyle para análise de code smells em repositórios Java.

## Estrutura de Arquivos

### Arquivos Principais

1. **`checkstyle_analyzer.py`**
   - **Localização**: `code_smell_study/core/checkstyle_analyzer.py`
   - **Função**: Classe principal que gerencia todo o processo de análise com o CheckStyle
   - **Detalhes**: Implementa a classe `CheckStyleAnalyzer` que:
     - Verifica a instalação do CheckStyle
     - Baixa o CheckStyle automaticamente se necessário
     - Executa a análise nos repositórios
     - Processa os resultados em formato JSON
     - Salva os relatórios de análise

2. **`run_checkstyle.py`**
   - **Localização**: `code_smell_study/run_checkstyle.py`
   - **Função**: Script para executar a análise de uma forma fácil via linha de comando
   - **Detalhes**:
     - Processa argumentos de linha de comando
     - Inicializa o analisador com os parâmetros corretos
     - Executa a análise em um ou mais repositórios
     - Gerencia logs e erros

3. **`run_all_checkstyle.bat`**
   - **Localização**: `code_smell_study/run_all_checkstyle.bat`
   - **Função**: Script batch para Windows que automatiza todo o processo
   - **Detalhes**:
     - Verifica dependências (Java, Python)
     - Configura os caminhos corretos
     - Baixa o CheckStyle se necessário
     - Cria a configuração se não existir
     - Executa a análise em todos os repositórios

5. **`checkstyle-config.xml`**
   - **Localização**: `code_smell_study/config/checkstyle-config.xml`
   - **Função**: Arquivo de configuração que define as regras para detecção de code smells
   - **Detalhes**:
     - Define limites para comprimento de métodos
     - Configura detecção de classes grandes
     - Estabelece limites de complexidade
     - Configura outras regras específicas para code smells

6. **`checkstyle.jar`**
   - **Localização**: `code_smell_study/config/checkstyle.jar`
   - **Função**: Arquivo JAR executável do CheckStyle
   - **Detalhes**:
     - É baixado automaticamente pelos scripts se não existir
     - Contém o programa CheckStyle que faz a análise estática do código
     - Versão 8.41 é usada para compatibilidade com Java 8

7. **`setup_checkstyle.bat`** (opcional)
   - **Localização**: `code_smell_study/setup_checkstyle.bat`
   - **Função**: Script para verificar e configurar o ambiente
   - **Detalhes**:
     - Verifica a instalação do Java
     - Cria os diretórios necessários
     - Verifica a existência da configuração

## Como Funciona

### Fluxo de Execução

1. **Verificação do Ambiente**:
   - Verifica se Java está instalado
   - Verifica se o CheckStyle está disponível (ou baixa automaticamente)
   - Verifica se a configuração existe (ou cria uma padrão)

2. **Análise dos Repositórios**:
   - Para cada repositório, o CheckStyle é executado nos arquivos Java
   - Os resultados são coletados em formato XML
   - O XML é processado e convertido para JSON

3. **Processamento dos Resultados**:
   - Os resultados são estruturados por tipo de code smell
   - Estatísticas são calculadas (contagens, severidade)
   - Os resultados são salvos em formato JSON para análise posterior

4. **Saída**:
   - Arquivos JSON na pasta `data/checkstyle/`
   - Um arquivo por repositório analisado
   - Cada arquivo contém os code smells detectados e estatísticas

### Tipos de Code Smells Detectados

O CheckStyle é configurado para detectar:

- **Long Method**: Métodos muito longos (> 60 linhas)
- **God Class**: Classes excessivamente grandes
- **Feature Envy**: Métodos que acessam mais dados de outras classes
- **Data Class**: Classes com muitos campos e poucos métodos
- **Magic Numbers**: Uso de números literais no código
- **Complexidade Ciclomática**: Métodos muito complexos
- **Muitos Parâmetros**: Métodos com muitos parâmetros

## Como Usar

### Execução Simples

A maneira mais fácil de executar a análise é usando o script batch:

```bash
.\run_all_checkstyle.bat
```

Este comando executa todo o processo automaticamente.

### Execução Personalizada

Para mais controle, você pode usar o script Python:

```bash
python run_checkstyle.py 
```

Opções disponíveis:
- `--repo-dir`: Diretório contendo os repositórios clonados
- `--config`: Caminho para o arquivo de configuração do CheckStyle
- `--jar`: Caminho para o JAR do CheckStyle
- `--output-dir`: Diretório onde serão salvos os resultados
- `--repo-name`: Nome de um repositório específico para analisar
- `--verbose`: Mostra informações detalhadas durante a execução

### Analisar um Único Repositório

Para analisar apenas um repositório específico:

```bash
python run_checkstyle.py --repo-name="doocs_advanced-java" --verbose
```

## Solução de Problemas

### Erro de Versão do Java

Se você encontrar erros relacionados à versão do Java:

```bash
python download_checkstyle_java8.py
```

Isso baixará uma versão do CheckStyle compatível com Java 8.

### "Saída Vazia do CheckStyle"

Se você receber erros de "Saída vazia":
- Verifique se o repositório contém arquivos Java
- Certifique-se que o CheckStyle está funcionando corretamente
- Execute com `--verbose` para ver mais detalhes

### Problemas de Importação

Se houver erros de importação no Python, a estrutura do projeto pode estar incorreta. Certifique-se de que:
- Você está no diretório correto
- A estrutura de diretórios está conforme descrita neste documento
- O PYTHONPATH inclui o diretório do projeto

## Personalização

### Configuração do CheckStyle

Você pode personalizar as regras editando o arquivo `config/checkstyle-config.xml`:

```xml
<module name="MethodLength">
    <property name="tokens" value="METHOD_DEF"/>
    <property name="max" value="60"/>  <!-- Altere este valor para mudar o limite -->
</module>
```

### Configuração da Saída

Os resultados são salvos em formato JSON, que pode ser facilmente processado por outras ferramentas ou scripts. A estrutura do JSON é:

```json
{
  "summary": {
    "total_issues": 1,
    "issues_by_severity": {"warning": 1},
    "issues_by_type": {"MethodLength": 1}
  },
  "repository": {
    "name": "nome_do_repositorio",
  }
}
```