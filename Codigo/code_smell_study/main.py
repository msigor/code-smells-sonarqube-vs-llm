import os
import json
import argparse
import sys
from pathlib import Path

# Adiciona o diretório atual ao PYTHONPATH para importações relativas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def carregar_dados_llm(arquivo_json=None, pasta_dados=None):
    """
    Carrega dados da LLM a partir de um arquivo JSON específico ou procura na pasta de dados
    """
    if arquivo_json and os.path.exists(arquivo_json):
        with open(arquivo_json, 'r') as f:
            return json.load(f)
    
    # Se não foi fornecido um arquivo específico, procura na pasta de dados
    if not pasta_dados:
        pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "llm")
    
    # Procura por arquivos JSON na pasta de dados
    arquivos_json = [f for f in os.listdir(pasta_dados) if f.endswith('.json')]
    
    if not arquivos_json:
        print(f"Erro: Nenhum arquivo JSON de LLM encontrado em {pasta_dados}")
        return {}
    
    # Usa o primeiro arquivo encontrado
    primeiro_arquivo = os.path.join(pasta_dados, arquivos_json[0])
    print(f"Usando dados LLM de: {primeiro_arquivo}")
    
    with open(primeiro_arquivo, 'r') as f:
        return json.load(f)

def carregar_dados_sonarqube(arquivo_json=None, pasta_dados=None):
    """
    Carrega dados do SonarQube a partir de um arquivo JSON específico ou procura na pasta de dados
    """
    if arquivo_json and os.path.exists(arquivo_json):
        with open(arquivo_json, 'r') as f:
            return json.load(f)
    
    # Se não foi fornecido um arquivo específico, procura na pasta de dados
    if not pasta_dados:
        pasta_dados = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sonarqube")
    
    # Procura por arquivos JSON na pasta de dados
    arquivos_json = [f for f in os.listdir(pasta_dados) if f.endswith('.json')]
    
    if not arquivos_json:
        print(f"Erro: Nenhum arquivo JSON de SonarQube encontrado em {pasta_dados}")
        return {}
    
    # Usa o primeiro arquivo encontrado
    primeiro_arquivo = os.path.join(pasta_dados, arquivos_json[0])
    print(f"Usando dados SonarQube de: {primeiro_arquivo}")
    
    with open(primeiro_arquivo, 'r') as f:
        return json.load(f)

def criar_pasta_resultados(pasta_resultados=None):
    """
    Cria a pasta de resultados se não existir
    """
    if not pasta_resultados:
        pasta_resultados = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    
    os.makedirs(pasta_resultados, exist_ok=True)
    return pasta_resultados

def main():
    """
    Função principal para executar a análise comparativa
    """
    parser = argparse.ArgumentParser(description='Análise Comparativa de Code Smells: LLM vs SonarQube')
    parser.add_argument('--llm', type=str, help='Caminho para o arquivo JSON com dados da LLM')
    parser.add_argument('--sonar', type=str, help='Caminho para o arquivo JSON com dados do SonarQube')
    parser.add_argument('--output', type=str, help='Pasta para salvar os resultados')
    
    args = parser.parse_args()
    
    # Importar o CodeSmellComparator
    try:
        # Tenta importar do módulo atual
        from core.code_smell_comparator import CodeSmellComparator
    except ImportError:
        # Se falhar, assume que o script está sendo executado como módulo
        try:
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from code_smell_study.core.code_smell_comparator import CodeSmellComparator
        except ImportError:
            print("Erro ao importar CodeSmellComparator. Certifique-se de que o arquivo code_smell_comparator.py está no mesmo diretório ou no PYTHONPATH.")
            sys.exit(1)
    
    # Carregar dados
    dados_llm = carregar_dados_llm(args.llm)
    dados_sonar = carregar_dados_sonarqube(args.sonar)
    
    if not dados_llm:
        # Dados de exemplo para LLM caso não seja encontrado
        dados_llm = {
           "smells_detectados": [
              "Long Method",
              "Magic Numbers",
              "Duplicated Logic"
           ],
           "descricao": {
              "Long Method": "Método computeCost muito extenso e complexo",
              "Magic Numbers": "Valores numéricos codificados diretamente no método",
              "Duplicated Logic": "Lógica de desconto e cálculo de preço repetitiva"
           },
           "localizacao": {
              "Long Method": "Pub.java:11-40",
              "Magic Numbers": "Pub.java:11-40",
              "Duplicated Logic": "Pub.java:11-40"
           },
           "confianca": {
              "Long Method": "alto",
              "Magic Numbers": "médio",
              "Duplicated Logic": "médio"
           }
        }
        print("Usando dados LLM de exemplo.")
    
    if not dados_sonar:
        print("Erro: Dados do SonarQube não encontrados. O programa será encerrado.")
        sys.exit(1)
    
    # Criar pasta de resultados
    pasta_resultados = criar_pasta_resultados(args.output)
    
    # Criar comparador e gerar relatório
    comparador = CodeSmellComparator(dados_llm, dados_sonar, pasta_resultados)
    resultados = comparador.generate_complete_report()
    
    print(f"Análise completa! Os resultados foram salvos em: {pasta_resultados}")
    print(f"Relatório detalhado disponível em: {os.path.join(pasta_resultados, 'relatorio_gqm.md')}")

if __name__ == "__main__":
    main()