import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
import seaborn as sns

class CodeSmellComparator:
    """
    Classe para comparar resultados de detecção de code smells entre LLM e SonarQube,
    seguindo o modelo GQM (Goal-Question-Metric) atualizado.
    """
    
    def __init__(self, llm_data, sonarqube_data, output_dir='./results', repo_name="repo"):
        """
        Inicializa o comparador com os dados das duas abordagens.
        
        Args:
            llm_data: Dados de code smells detectados por LLMs
            sonarqube_data: Dados de code smells detectados por SonarQube
            output_dir: Diretório para salvar resultados e gráficos
            repo_name: Nome do repositório sendo analisado
        """
        self.llm_data = self._normalize_llm_data(llm_data)
        self.sonarqube_data = self._normalize_sonarqube_data(sonarqube_data)
        self.output_dir = output_dir
        self.repo_name = repo_name
        os.makedirs(output_dir, exist_ok=True)
        
        # Mapear categorias para normalização
        self.categories_mapping = {
            # LLM -> Categorias padronizadas
            "Long Method": "Long Method",
            "God Class": "God Class",
            "God Object": "God Class",
            "Large Class": "God Class",
            "Duplicate Code": "Duplicate Code",
            "Duplicated Logic": "Duplicate Code",
            "Magic Numbers": "Magic Numbers",
            "Feature Envy": "Feature Envy",
            "Data Class": "Data Class",
            "Exception Handling": "Exception Handling",
            
            # SonarQube -> Categorias padronizadas
            "java:S1192": "Duplicate Code",      # String literals should not be duplicated
            "java:S112": "Exception Handling",   # Generic exceptions should not be thrown
            "java:S1130": "Exception Handling",  # Remove unnecessary thrown exceptions
            "java:S138": "Long Method",          # Methods should not have too many lines
            "java:S1448": "God Class",           # Classes should not have too many methods
            "java:S1200": "God Class",           # Classes should not be too complex
            "java:S109": "Magic Numbers",        # Magic numbers should not be used
            "java:S3400": "Magic Numbers",       # Methods should not return constants
            "java:S1144": "Magic Numbers",       # Unused private methods should be removed
            "java:S1172": "Feature Envy",        # Unused method parameters should be removed
            "java:S1104": "Data Class",          # Class variable visibility should be reduced
            "java:S1450": "Data Class"           # Private class members should not be exposed
        }
        
        # Extrair informações para análise
        self._extract_smells_and_files()
        
    def _normalize_llm_data(self, data):
        """Normaliza os dados do LLM para o formato padrão"""
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                print("Erro ao fazer parse do JSON do LLM")
                return {}
        return data
    
    def _normalize_sonarqube_data(self, data):
        """Normaliza os dados do SonarQube para o formato padrão"""
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                print("Erro ao fazer parse do JSON do SonarQube")
                return {}
        return data
    
    def _extract_smells_and_files(self):
        """Extrai informações de smells e arquivos para facilitar a análise"""
        # Para LLM
        self.llm_smells = []
        self.llm_files = set()
        
        if isinstance(self.llm_data, dict) and "smells_detectados" in self.llm_data:
            # Como não temos informações de arquivo, usamos um arquivo padrão
            default_file = f"{self.repo_name}_file.java"
            self.llm_files.add(default_file)
            
            # Para cada smell detectado
            for smell_type in self.llm_data["smells_detectados"]:
                # Normalizar categoria
                normalized_category = self.categories_mapping.get(smell_type, "Outros")
                
                # Extrair confiança - já está no formato correto
                confidence = "médio"
                if "confianca" in self.llm_data and smell_type in self.llm_data["confianca"]:
                    confidence = self.llm_data["confianca"][smell_type]
                
                # Descrição geral para todos os smells
                description = ""
                if "descricao" in self.llm_data:
                    description = self.llm_data["descricao"]
                
                self.llm_smells.append({
                    "category": normalized_category,
                    "original_category": smell_type,
                    "file": default_file,
                    "lines": [],
                    "description": description,
                    "confidence": confidence
                })
        
        # Para SonarQube
        self.sonar_smells = []
        self.sonar_files = set()
        
        if isinstance(self.sonarqube_data, dict) and "issues" in self.sonarqube_data:
            for issue in self.sonarqube_data["issues"]:
                if issue.get("type") == "CODE_SMELL":
                    rule = issue.get("rule", "")
                    
                    # Normalizar categoria
                    normalized_category = self.categories_mapping.get(rule, "Outros")
                    
                    # Extrair componente (arquivo)
                    component = issue.get("component", "")
                    file_name = component.split(":")[-1] if ":" in component else component
                    
                    if not file_name:
                        file_name = f"{self.repo_name}_file.java"
                    
                    if file_name:
                        self.sonar_files.add(file_name)
                    
                    self.sonar_smells.append({
                        "category": normalized_category,
                        "original_category": rule,
                        "file": file_name,
                        "lines": [],
                        "message": issue.get("message", ""),
                        "severity": issue.get("severity", "")
                    })
        
        # União de todos os arquivos relevantes
        self.all_files = self.llm_files.union(self.sonar_files)
        
    def question1_analysis(self):
        """
        Análise da Questão 1: Qual das duas abordagens detecta mais code smells clássicos?
        Métricas:
        - 1.1: Número total de code smells detectados pela LLM e pelo SonarQube
        - 1.2: Média de code smells detectados por repositório (simulado como por arquivo neste caso)
        - 1.3: Diferença média de detecção por repositório entre as abordagens
        """
        results = {}
        
        # Métrica 1.1: Número total de code smells
        llm_count = len(self.llm_smells)
        sonar_count = len(self.sonar_smells)
        
        results["metrica_1_1"] = {
            "llm_total": llm_count,
            "sonarqube_total": sonar_count,
            "diferenca_absoluta": abs(llm_count - sonar_count),
            "relacao_percentual": (llm_count / sonar_count * 100) if sonar_count > 0 else float('inf')
        }
        
        # Métrica 1.2: Média de code smells por "repositório" (simulamos como por arquivo)
        # Contamos smells por arquivo para cada abordagem
        llm_smells_por_arquivo = defaultdict(int)
        sonar_smells_por_arquivo = defaultdict(int)
        
        for smell in self.llm_smells:
            if smell["file"]:
                llm_smells_por_arquivo[smell["file"]] += 1
                
        for smell in self.sonar_smells:
            if smell["file"]:
                sonar_smells_por_arquivo[smell["file"]] += 1
        
        # Calculamos as médias
        llm_media_por_arquivo = sum(llm_smells_por_arquivo.values()) / len(llm_smells_por_arquivo) if llm_smells_por_arquivo else 0
        sonar_media_por_arquivo = sum(sonar_smells_por_arquivo.values()) / len(sonar_smells_por_arquivo) if sonar_smells_por_arquivo else 0
        
        results["metrica_1_2"] = {
            "llm_media_por_arquivo": llm_media_por_arquivo,
            "sonarqube_media_por_arquivo": sonar_media_por_arquivo,
            "arquivos_com_smells_llm": len(llm_smells_por_arquivo),
            "arquivos_com_smells_sonarqube": len(sonar_smells_por_arquivo)
        }
        
        # Métrica 1.3: Diferença média de detecção
        # Para cada arquivo que aparece em ambas as abordagens, calculamos a diferença
        arquivos_comuns = set(llm_smells_por_arquivo.keys()).intersection(set(sonar_smells_por_arquivo.keys()))
        
        diferencas = []
        for arquivo in arquivos_comuns:
            diferenca = abs(llm_smells_por_arquivo[arquivo] - sonar_smells_por_arquivo[arquivo])
            diferencas.append(diferenca)
        
        diferenca_media = sum(diferencas) / len(diferencas) if diferencas else 0
        
        results["metrica_1_3"] = {
            "diferenca_media_por_arquivo": diferenca_media,
            "arquivos_comuns": len(arquivos_comuns),
            "diferencas_por_arquivo": {arquivo: abs(llm_smells_por_arquivo[arquivo] - sonar_smells_por_arquivo[arquivo]) 
                                       for arquivo in arquivos_comuns}
        }
        
        # Gerar gráficos
        self._plot_question1_results(results)
        
        return results
    
    def _plot_question1_results(self, results):
        """Gera gráficos para a Questão 1"""
        # Gráfico para total de smells
        plt.figure(figsize=(10, 6))
        plt.bar(['LLM', 'SonarQube'], 
                [results["metrica_1_1"]["llm_total"], results["metrica_1_1"]["sonarqube_total"]], 
                color=['#3498db', '#e74c3c'])
        plt.title('Número Total de Code Smells Detectados')
        plt.ylabel('Quantidade de Code Smells')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/q1_total_smells.png")
        plt.close()
        
        # Gráfico para média por arquivo
        plt.figure(figsize=(10, 6))
        plt.bar(['LLM', 'SonarQube'], 
                [results["metrica_1_2"]["llm_media_por_arquivo"], results["metrica_1_2"]["sonarqube_media_por_arquivo"]], 
                color=['#3498db', '#e74c3c'])
        plt.title('Média de Code Smells por Arquivo')
        plt.ylabel('Média de Code Smells')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/q1_media_por_arquivo.png")
        plt.close()
        
        # Gráfico para diferença por arquivo comum
        if results["metrica_1_3"]["arquivos_comuns"] > 0:
            diferencas = results["metrica_1_3"]["diferencas_por_arquivo"]
            arquivos = list(diferencas.keys())
            valores = list(diferencas.values())
            
            # Limitamos a 15 arquivos no gráfico para legibilidade
            if len(arquivos) > 15:
                # Ordena por diferença e pega os 15 com maior diferença
                sorted_items = sorted(diferencas.items(), key=lambda x: x[1], reverse=True)[:15]
                arquivos = [item[0] for item in sorted_items]
                valores = [item[1] for item in sorted_items]
            
            plt.figure(figsize=(12, 6))
            plt.bar(arquivos, valores, color='#2ecc71')
            plt.title('Diferença de Detecção por Arquivo')
            plt.ylabel('Diferença Absoluta')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/q1_diferenca_por_arquivo.png")
            plt.close()
    
    def question2_analysis(self):
        """
        Análise da Questão 2: As duas abordagens convergem ou divergem nos resultados?
        Métricas:
        - 2.1: Porcentagem de smells detectados simultaneamente por ambas as abordagens
        - 2.2: Porcentagem de smells exclusivos de cada abordagem
        - 2.3: Número de repositórios com alta/baixa sobreposição
        """
        results = {}
        
        # Criamos fingerprints para cada smell para facilitar a comparação
        llm_fingerprints = set()
        sonar_fingerprints = set()
        
        for smell in self.llm_smells:
            llm_fingerprints.add(f"{smell['category']}")
        
        for smell in self.sonar_smells:
            sonar_fingerprints.add(f"{smell['category']}")
        
        # Calcular intersecção e união
        intersecao = llm_fingerprints.intersection(sonar_fingerprints)
        uniao = llm_fingerprints.union(sonar_fingerprints)
        
        # Métrica 2.1: Porcentagem de smells detectados simultaneamente
        if len(uniao) > 0:
            taxa_similaridade = (len(intersecao) / len(uniao)) * 100
        else:
            taxa_similaridade = 0
        
        results["metrica_2_1"] = {
            "smells_comuns": len(intersecao),
            "total_smells_unicos": len(uniao),
            "taxa_similaridade_percentual": taxa_similaridade
        }
        
        # Métrica 2.2: Porcentagem de smells exclusivos
        llm_exclusivos = llm_fingerprints - sonar_fingerprints
        sonar_exclusivos = sonar_fingerprints - llm_fingerprints
        
        if len(uniao) > 0:
            taxa_exclusividade_llm = (len(llm_exclusivos) / len(uniao)) * 100
            taxa_exclusividade_sonar = (len(sonar_exclusivos) / len(uniao)) * 100
        else:
            taxa_exclusividade_llm = 0
            taxa_exclusividade_sonar = 0
        
        results["metrica_2_2"] = {
            "llm_exclusivos": len(llm_exclusivos),
            "sonar_exclusivos": len(sonar_exclusivos),
            "taxa_exclusividade_llm": taxa_exclusividade_llm,
            "taxa_exclusividade_sonar": taxa_exclusividade_sonar
        }
        
        # Métrica 2.3: Classificação da sobreposição
        # Como não temos arquivos específicos, simulamos por categorias
        categorias = list(uniao)
        sobreposicao_por_categoria = {}
        
        for categoria in categorias:
            # Calculamos a taxa de sobreposição para esta categoria
            llm_has = categoria in llm_fingerprints
            sonar_has = categoria in sonar_fingerprints
            
            if llm_has and sonar_has:
                sobreposicao_por_categoria[categoria] = 100.0  # 100% de sobreposição
            else:
                sobreposicao_por_categoria[categoria] = 0.0  # 0% de sobreposição
        
        # Contamos categorias com alta e baixa sobreposição
        alta_sobreposicao = sum(1 for taxa in sobreposicao_por_categoria.values() if taxa >= 80)
        baixa_sobreposicao = sum(1 for taxa in sobreposicao_por_categoria.values() if taxa <= 20)
        
        results["metrica_2_3"] = {
            "categorias_alta_sobreposicao": alta_sobreposicao,
            "categorias_baixa_sobreposicao": baixa_sobreposicao,
            "total_categorias": len(sobreposicao_por_categoria),
            "sobreposicao_por_categoria": sobreposicao_por_categoria
        }
        
        # Gerar gráficos
        self._plot_question2_results(results, categorias)
        
        return results
    
    def _plot_question2_results(self, results, categorias):
        """Gera gráficos para a Questão 2"""
        # Gráfico para distribuição de smells (comuns e exclusivos)
        plt.figure(figsize=(10, 6))
        plt.bar(['Exclusivos LLM', 'Comuns', 'Exclusivos SonarQube'], 
                [results["metrica_2_2"]["llm_exclusivos"], 
                 results["metrica_2_1"]["smells_comuns"], 
                 results["metrica_2_2"]["sonar_exclusivos"]], 
                color=['#3498db', '#2ecc71', '#e74c3c'])
        plt.title('Distribuição de Code Smells Detectados')
        plt.ylabel('Número de Code Smells')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/q2_distribuicao_smells.png")
        plt.close()
        
        # Gráfico para taxa de similaridade/exclusividade
        plt.figure(figsize=(10, 6))
        plt.bar(['Similaridade', 'Exclusivos LLM', 'Exclusivos SonarQube'], 
                [results["metrica_2_1"]["taxa_similaridade_percentual"],
                 results["metrica_2_2"]["taxa_exclusividade_llm"],
                 results["metrica_2_2"]["taxa_exclusividade_sonar"]], 
                color=['#2ecc71', '#3498db', '#e74c3c'])
        plt.title('Taxas de Similaridade e Exclusividade (%)')
        plt.ylabel('Porcentagem (%)')
        plt.ylim(0, 100)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/q2_taxas_percentuais.png")
        plt.close()
        
        # Gráfico para sobreposição por categoria
        if categorias:
            sobreposicao = results["metrica_2_3"]["sobreposicao_por_categoria"]
            categorias_nomes = list(sobreposicao.keys())
            valores = list(sobreposicao.values())
            
            plt.figure(figsize=(12, 6))
            plt.bar(categorias_nomes, valores, color='#f39c12')
            plt.axhline(y=80, color='g', linestyle='--', label='Alta Sobreposição (80%)')
            plt.axhline(y=20, color='r', linestyle='--', label='Baixa Sobreposição (20%)')
            plt.title('Taxa de Sobreposição por Categoria (%)')
            plt.ylabel('Sobreposição (%)')
            plt.ylim(0, 100)
            plt.xticks(rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            plt.savefig(f"{self.output_dir}/q2_sobreposicao_por_categoria.png")
            plt.close()
    
    def question3_analysis(self):
        """
        Análise da Questão 3: Existem categorias de smells mais detectadas por cada abordagem?
        Métricas:
        - 3.1: Número médio de smells por categoria para cada abordagem
        - 3.2: Porcentagem de smells simultâneos por categoria
        - 3.3: Porcentagem de smells exclusivos por categoria
        """
        results = {}
        
        # Definimos categorias para análise
        categorias = set()
        for smell in self.llm_smells:
            categorias.add(smell["category"])
        for smell in self.sonar_smells:
            categorias.add(smell["category"])
        
        # Ordenamos para consistência
        categorias = sorted(list(categorias))
        
        # Contagem de smells por categoria para cada abordagem
        llm_por_categoria = defaultdict(int)
        sonar_por_categoria = defaultdict(int)
        
        for smell in self.llm_smells:
            llm_por_categoria[smell["category"]] += 1
            
        for smell in self.sonar_smells:
            sonar_por_categoria[smell["category"]] += 1
        
        # Métrica 3.1: Número médio de smells por categoria
        # Calculamos a média apenas para categorias onde há detecções
        llm_categorias_com_deteccao = sum(1 for count in llm_por_categoria.values() if count > 0)
        sonar_categorias_com_deteccao = sum(1 for count in sonar_por_categoria.values() if count > 0)
        
        llm_media_por_categoria = sum(llm_por_categoria.values()) / llm_categorias_com_deteccao if llm_categorias_com_deteccao > 0 else 0
        sonar_media_por_categoria = sum(sonar_por_categoria.values()) / sonar_categorias_com_deteccao if sonar_categorias_com_deteccao > 0 else 0
        
        results["metrica_3_1"] = {
            "llm_media_por_categoria": llm_media_por_categoria,
            "sonarqube_media_por_categoria": sonar_media_por_categoria,
            "llm_por_categoria": dict(llm_por_categoria),
            "sonarqube_por_categoria": dict(sonar_por_categoria)
        }
        
        # Métricas 3.2 e 3.3: Smells simultâneos e exclusivos por categoria
        # Calculamos baseados apenas na presença da categoria
        simultaneos_por_categoria = {}
        exclusivos_llm_por_categoria = {}
        exclusivos_sonar_por_categoria = {}
        percentual_simultaneos_por_categoria = {}
        percentual_exclusivos_llm_por_categoria = {}
        percentual_exclusivos_sonar_por_categoria = {}
        
        for categoria in categorias:
            llm_tem = llm_por_categoria[categoria] > 0
            sonar_tem = sonar_por_categoria[categoria] > 0
            
            # Determinamos se a categoria é detectada por ambas as abordagens
            simultaneo = llm_tem and sonar_tem
            exclusivo_llm = llm_tem and not sonar_tem
            exclusivo_sonar = sonar_tem and not llm_tem
            
            # Armazenamos contagens como 0 ou 1 (percentual será 0% ou 100%)
            simultaneos_por_categoria[categoria] = 1 if simultaneo else 0
            exclusivos_llm_por_categoria[categoria] = 1 if exclusivo_llm else 0
            exclusivos_sonar_por_categoria[categoria] = 1 if exclusivo_sonar else 0
            
            # Percentuais são 0% ou 100%
            if llm_tem or sonar_tem:  # Se pelo menos uma abordagem detectou
                percentual_simultaneos_por_categoria[categoria] = 100.0 if simultaneo else 0.0
                percentual_exclusivos_llm_por_categoria[categoria] = 100.0 if exclusivo_llm else 0.0
                percentual_exclusivos_sonar_por_categoria[categoria] = 100.0 if exclusivo_sonar else 0.0
            else:
                percentual_simultaneos_por_categoria[categoria] = 0.0
                percentual_exclusivos_llm_por_categoria[categoria] = 0.0
                percentual_exclusivos_sonar_por_categoria[categoria] = 0.0
        
        results["metrica_3_2"] = {
            "simultaneos_por_categoria": simultaneos_por_categoria,
            "percentual_simultaneos_por_categoria": percentual_simultaneos_por_categoria
        }
        
        results["metrica_3_3"] = {
            "exclusivos_llm_por_categoria": exclusivos_llm_por_categoria,
            "exclusivos_sonar_por_categoria": exclusivos_sonar_por_categoria,
            "percentual_exclusivos_llm_por_categoria": percentual_exclusivos_llm_por_categoria,
            "percentual_exclusivos_sonar_por_categoria": percentual_exclusivos_sonar_por_categoria
        }
        
        # Gerar gráficos
        self._plot_question3_results(results, categorias)
        
        return results, categorias
    
    def _plot_question3_results(self, results, categorias):
        """Gera gráficos para a Questão 3"""
        # Gráfico para contagem por categoria
        plt.figure(figsize=(12, 8))
        x = np.arange(len(categorias))
        width = 0.35
        
        plt.bar(x - width/2, [results["metrica_3_1"]["llm_por_categoria"].get(c, 0) for c in categorias], 
                width, label='LLM', color='#3498db')
        plt.bar(x + width/2, [results["metrica_3_1"]["sonarqube_por_categoria"].get(c, 0) for c in categorias], 
                width, label='SonarQube', color='#e74c3c')
        
        plt.xlabel('Categoria de Code Smell')
        plt.ylabel('Número de Smells Detectados')
        plt.title('Detecção de Code Smells por Categoria')
        plt.xticks(x, categorias, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/q3_contagem_por_categoria.png")
        plt.close()
        
        # Gráfico para percentual de similaridade por categoria
        plt.figure(figsize=(12, 8))
        
        # Extraímos os dados para o gráfico empilhado
        simultaneos = [results["metrica_3_2"]["percentual_simultaneos_por_categoria"].get(c, 0) for c in categorias]
        exclusivos_llm = [results["metrica_3_3"]["percentual_exclusivos_llm_por_categoria"].get(c, 0) for c in categorias]
        exclusivos_sonar = [results["metrica_3_3"]["percentual_exclusivos_sonar_por_categoria"].get(c, 0) for c in categorias]
        
        # Criamos o gráfico empilhado corrigido
        x = np.arange(len(categorias))
        width = 0.8
        
        # Convertemos para arrays numpy para facilitar a soma
        exc_llm_arr = np.array(exclusivos_llm)
        sim_arr = np.array(simultaneos)
        
        # Criamos as barras empilhadas
        plt.bar(x, exclusivos_llm, width, label='Exclusivos LLM', color='#3498db')
        plt.bar(x, simultaneos, width, bottom=exc_llm_arr, label='Simultâneos', color='#2ecc71')
        plt.bar(x, exclusivos_sonar, width, bottom=exc_llm_arr + sim_arr, label='Exclusivos SonarQube', color='#e74c3c')
        
        plt.xlabel('Categoria de Code Smell')
        plt.ylabel('Percentual de Smells (%)')
        plt.title('Distribuição de Smells por Categoria')
        plt.xticks(x, categorias, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/q3_percentual_por_categoria.png")
        plt.close()
        
        # Gráfico de heat map para visualizar a distribuição de detecções
        plt.figure(figsize=(12, 8))
        
        # Criamos uma matriz para o heatmap
        data = []
        for c in categorias:
            data.append([
                results["metrica_3_1"]["llm_por_categoria"].get(c, 0),
                results["metrica_3_1"]["sonarqube_por_categoria"].get(c, 0),
                results["metrica_3_2"]["simultaneos_por_categoria"].get(c, 0)
            ])
        
        # Convertemos para array numpy
        data_array = np.array(data)
        
        # Criamos o heatmap
        ax = sns.heatmap(data_array, 
                         annot=True, 
                         fmt="d", 
                         cmap="YlGnBu",
                         xticklabels=['LLM', 'SonarQube', 'Simultâneos'],
                         yticklabels=categorias)
        
        plt.title('Distribuição de Detecções por Categoria e Abordagem')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/q3_heatmap_categorias.png")
        plt.close()
    
    def generate_complete_report(self):
        """
        Gera um relatório completo com todas as análises para o modelo GQM atualizado
        """
        # Executar todas as análises
        print("Gerando análises para as 3 perguntas do GQM atualizado...")
        
        q1_results = self.question1_analysis()
        q2_results = self.question2_analysis()
        q3_results, categorias = self.question3_analysis()
        
        # Consolidar resultados
        results = {
            "repositorio": self.repo_name,
            "question1": q1_results,
            "question2": q2_results,
           "question3": q3_results,
            "categorias": list(categorias)
        }
        
        # Salvar resultados em JSON
        with open(f"{self.output_dir}/resultados_gqm.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Relatório completo gerado com sucesso em {self.output_dir}")
        
        # Gerar tabelas para o relatório em formato markdown
        self._generate_markdown_report(results, categorias)
        
        return results
    
    def _generate_markdown_report(self, results, categorias):
        """
        Gera um relatório em formato markdown com os resultados do GQM atualizado
        """
        with open(f"{self.output_dir}/relatorio_gqm.md", 'w') as f:
            f.write("# Relatório GQM: Comparação entre LLM e SonarQube na Detecção de Code Smells\n\n")
            f.write(f"Repositório analisado: **{self.repo_name}**\n\n")
            
            # Pergunta 1
            f.write("## Questão 1: Qual das duas abordagens detecta mais code smells clássicos?\n\n")
            
            # Métrica 1.1: Total de code smells
            f.write("### Métrica 1.1: Número total de code smells detectados\n\n")
            f.write("| Abordagem | Quantidade de Smells |\n")
            f.write("|-----------|----------------------|\n")
            f.write(f"| LLM | {results['question1']['metrica_1_1']['llm_total']} |\n")
            f.write(f"| SonarQube | {results['question1']['metrica_1_1']['sonarqube_total']} |\n")
            f.write(f"| Diferença absoluta | {results['question1']['metrica_1_1']['diferenca_absoluta']} |\n")
            f.write(f"| Relação percentual (LLM/SonarQube) | {results['question1']['metrica_1_1']['relacao_percentual']:.2f}% |\n\n")
            
            # Métrica 1.2: Média por arquivo
            f.write("### Métrica 1.2: Média de code smells detectados por arquivo\n\n")
            f.write("| Abordagem | Média de Smells por Arquivo | Arquivos com Smells |\n")
            f.write("|-----------|------------------------------|---------------------|\n")
            f.write(f"| LLM | {results['question1']['metrica_1_2']['llm_media_por_arquivo']:.2f} | {results['question1']['metrica_1_2']['arquivos_com_smells_llm']} |\n")
            f.write(f"| SonarQube | {results['question1']['metrica_1_2']['sonarqube_media_por_arquivo']:.2f} | {results['question1']['metrica_1_2']['arquivos_com_smells_sonarqube']} |\n\n")
            
            # Métrica 1.3: Diferença média
            f.write("### Métrica 1.3: Diferença média de detecção por arquivo\n\n")
            f.write(f"- Diferença média por arquivo: **{results['question1']['metrica_1_3']['diferenca_media_por_arquivo']:.2f}**\n")
            f.write(f"- Número de arquivos comuns analisados: **{results['question1']['metrica_1_3']['arquivos_comuns']}**\n\n")
            
            f.write("![Total de Code Smells](./q1_total_smells.png)\n\n")
            f.write("![Média por Arquivo](./q1_media_por_arquivo.png)\n\n")
            if results['question1']['metrica_1_3']['arquivos_comuns'] > 0:
                f.write("![Diferença por Arquivo](./q1_diferenca_por_arquivo.png)\n\n")
            
            # Pergunta 2
            f.write("## Questão 2: As duas abordagens convergem ou divergem nos resultados?\n\n")
            
            # Métrica 2.1: Smells simultâneos
            f.write("### Métrica 2.1: Porcentagem de smells detectados simultaneamente\n\n")
            f.write("| Métrica | Valor |\n")
            f.write("|---------|-------|\n")
            f.write(f"| Smells detectados por ambas abordagens | {results['question2']['metrica_2_1']['smells_comuns']} |\n")
            f.write(f"| Total de smells únicos (união) | {results['question2']['metrica_2_1']['total_smells_unicos']} |\n")
            f.write(f"| Taxa de similaridade | {results['question2']['metrica_2_1']['taxa_similaridade_percentual']:.2f}% |\n\n")
            
            # Métrica 2.2: Smells exclusivos
            f.write("### Métrica 2.2: Porcentagem de smells exclusivos\n\n")
            f.write("| Métrica | Valor |\n")
            f.write("|---------|-------|\n")
            f.write(f"| Smells exclusivos LLM | {results['question2']['metrica_2_2']['llm_exclusivos']} |\n")
            f.write(f"| Smells exclusivos SonarQube | {results['question2']['metrica_2_2']['sonar_exclusivos']} |\n")
            f.write(f"| Taxa de exclusividade LLM | {results['question2']['metrica_2_2']['taxa_exclusividade_llm']:.2f}% |\n")
            f.write(f"| Taxa de exclusividade SonarQube | {results['question2']['metrica_2_2']['taxa_exclusividade_sonar']:.2f}% |\n\n")
            
            # Métrica 2.3: Sobreposição
            f.write("### Métrica 2.3: Número de categorias com alta/baixa sobreposição\n\n")
            f.write("| Métrica | Valor |\n")
            f.write("|---------|-------|\n")
            f.write(f"| Categorias com alta sobreposição (>80%) | {results['question2']['metrica_2_3']['categorias_alta_sobreposicao']} |\n")
            f.write(f"| Categorias com baixa sobreposição (<20%) | {results['question2']['metrica_2_3']['categorias_baixa_sobreposicao']} |\n")
            f.write(f"| Total de categorias analisadas | {results['question2']['metrica_2_3']['total_categorias']} |\n\n")
            
            f.write("![Distribuição de Smells](./q2_distribuicao_smells.png)\n\n")
            f.write("![Taxas Percentuais](./q2_taxas_percentuais.png)\n\n")
            if 'categorias' in results and results['categorias']:
                f.write("![Sobreposição por Categoria](./q2_sobreposicao_por_categoria.png)\n\n")
            
            # Pergunta 3
            f.write("## Questão 3: Existem categorias de smells mais detectadas por cada abordagem?\n\n")
            
            # Métrica 3.1: Smells por categoria
            f.write("### Métrica 3.1: Número médio de smells por categoria\n\n")
            f.write(f"- LLM: média de **{results['question3']['metrica_3_1']['llm_media_por_categoria']:.2f}** smells por categoria\n")
            f.write(f"- SonarQube: média de **{results['question3']['metrica_3_1']['sonarqube_media_por_categoria']:.2f}** smells por categoria\n\n")
            
            f.write("| Categoria | LLM | SonarQube |\n")
            f.write("|-----------|-----|----------|\n")
            for c in categorias:
                llm_count = results['question3']['metrica_3_1']['llm_por_categoria'].get(c, 0)
                sonar_count = results['question3']['metrica_3_1']['sonarqube_por_categoria'].get(c, 0)
                f.write(f"| {c} | {llm_count} | {sonar_count} |\n")
            f.write("\n")
            
            # Métrica 3.2: Smells simultâneos por categoria
            f.write("### Métrica 3.2: Porcentagem de smells simultâneos por categoria\n\n")
            f.write("| Categoria | Número de Smells Simultâneos | % de Simultaneidade |\n")
            f.write("|-----------|------------------------------|--------------------|\n")
            for c in categorias:
                count = results['question3']['metrica_3_2']['simultaneos_por_categoria'].get(c, 0)
                percent = results['question3']['metrica_3_2']['percentual_simultaneos_por_categoria'].get(c, 0)
                f.write(f"| {c} | {count} | {percent:.2f}% |\n")
            f.write("\n")
            
            # Métrica 3.3: Smells exclusivos por categoria
            f.write("### Métrica 3.3: Porcentagem de smells exclusivos por categoria\n\n")
            f.write("| Categoria | Exclusivos LLM | % LLM | Exclusivos SonarQube | % SonarQube |\n")
            f.write("|-----------|----------------|-------|---------------------|-------------|\n")
            for c in categorias:
                llm_count = results['question3']['metrica_3_3']['exclusivos_llm_por_categoria'].get(c, 0)
                sonar_count = results['question3']['metrica_3_3']['exclusivos_sonar_por_categoria'].get(c, 0)
                llm_percent = results['question3']['metrica_3_3']['percentual_exclusivos_llm_por_categoria'].get(c, 0)
                sonar_percent = results['question3']['metrica_3_3']['percentual_exclusivos_sonar_por_categoria'].get(c, 0)
                f.write(f"| {c} | {llm_count} | {llm_percent:.2f}% | {sonar_count} | {sonar_percent:.2f}% |\n")
            f.write("\n")
            
            f.write("![Contagem por Categoria](./q3_contagem_por_categoria.png)\n\n")
            f.write("![Percentual por Categoria](./q3_percentual_por_categoria.png)\n\n")
            f.write("![Heatmap de Categorias](./q3_heatmap_categorias.png)\n\n")
            
            # Conclusões
            f.write("## Conclusões\n\n")
            
            # Questão 1 - Conclusão
            llm_count = results['question1']['metrica_1_1']['llm_total']
            sonar_count = results['question1']['metrica_1_1']['sonarqube_total']
            
            f.write("### Questão 1: Qual das duas abordagens detecta mais code smells clássicos?\n\n")
            if llm_count > sonar_count:
                f.write(f"A abordagem LLM detectou mais code smells ({llm_count}) em comparação com o SonarQube ({sonar_count}). ")
            elif sonar_count > llm_count:
                f.write(f"O SonarQube detectou mais code smells ({sonar_count}) em comparação com a abordagem LLM ({llm_count}). ")
            else:
                f.write(f"Ambas as abordagens detectaram o mesmo número de code smells ({llm_count}). ")
                
            f.write(f"A diferença média por arquivo foi de {results['question1']['metrica_1_3']['diferenca_media_por_arquivo']:.2f} smells, ")
            f.write("o que indica uma discrepância significativa entre as abordagens na detecção em nível de arquivo.\n\n")
            
            # Questão 2 - Conclusão
            taxa_similaridade = results['question2']['metrica_2_1']['taxa_similaridade_percentual']
            
            f.write("### Questão 2: As duas abordagens convergem ou divergem nos resultados?\n\n")
            f.write(f"A taxa de similaridade entre as abordagens foi de {taxa_similaridade:.2f}%, ")
            
            if taxa_similaridade < 30:
                f.write("indicando uma **alta divergência** entre os resultados. ")
            elif taxa_similaridade < 70:
                f.write("indicando uma **divergência moderada** entre os resultados. ")
            else:
                f.write("indicando uma **boa convergência** entre os resultados. ")
            
            f.write(f"Das {results['question2']['metrica_2_3']['total_categorias']} categorias analisadas, ")
            f.write(f"{results['question2']['metrica_2_3']['categorias_alta_sobreposicao']} apresentaram alta sobreposição (>80%) ")
            f.write(f"e {results['question2']['metrica_2_3']['categorias_baixa_sobreposicao']} apresentaram baixa sobreposição (<20%).\n\n")
            
            # Questão 3 - Conclusão
            f.write("### Questão 3: Existem categorias de smells mais detectadas por cada abordagem?\n\n")
            
            # Identificar categorias predominantes em cada abordagem
            llm_cats = sorted(results['question3']['metrica_3_1']['llm_por_categoria'].items(), 
                              key=lambda x: x[1], reverse=True)
            sonar_cats = sorted(results['question3']['metrica_3_1']['sonarqube_por_categoria'].items(), 
                                key=lambda x: x[1], reverse=True)
            
            if llm_cats:
                f.write(f"A LLM detectou mais frequentemente smells da categoria **{llm_cats[0][0]}** ")
                f.write(f"com {llm_cats[0][1]} ocorrências. ")
            
            if sonar_cats:
                f.write(f"O SonarQube detectou mais frequentemente smells da categoria **{sonar_cats[0][0]}** ")
                f.write(f"com {sonar_cats[0][1]} ocorrências.\n\n")
            
            # Identificar categorias com maior divergência
            max_divergencia = 0
            categoria_divergente = None
            
            for c in categorias:
                llm_percent = results['question3']['metrica_3_3']['percentual_exclusivos_llm_por_categoria'].get(c, 0)
                sonar_percent = results['question3']['metrica_3_3']['percentual_exclusivos_sonar_por_categoria'].get(c, 0)
                divergencia = llm_percent + sonar_percent
                
                if divergencia > max_divergencia:
                    max_divergencia = divergencia
                    categoria_divergente = c
            
            if categoria_divergente:
                f.write(f"A categoria com maior divergência entre as abordagens foi **{categoria_divergente}**, ")
                f.write(f"com {max_divergencia:.2f}% de detecções exclusivas somadas.\n\n")
            
            # Recomendações finais
            f.write("## Recomendações\n\n")
            f.write("Com base na análise realizada, recomenda-se:\n\n")
            
            f.write("1. **Abordagem complementar**: Utilizar ambas as ferramentas em conjunto, já que apresentam ")
            f.write(f"uma taxa de similaridade de apenas {taxa_similaridade:.2f}%, complementando-se na detecção.\n\n")
            
            f.write("2. **Foco em categorias específicas**: A LLM mostrou maior eficácia na detecção de ")
            if llm_cats:
                f.write(f"smells do tipo **{llm_cats[0][0]}**, ")
            f.write("enquanto o SonarQube se destacou em ")
            if sonar_cats:
                f.write(f"**{sonar_cats[0][0]}**. ")
            f.write("Considerar essa especialização ao escolher a ferramenta adequada.\n\n")
            
            f.write("3. **Validação humana**: Para as categorias com baixa sobreposição entre as ferramentas, ")
            f.write("é recomendada uma revisão manual para validar os resultados e identificar os falsos positivos.\n\n")

            f.write("4. **Refinamento de prompts**: Os resultados sugerem oportunidades para aprimorar a engenharia de prompts ")
            f.write("para as LLMs, especialmente nas categorias onde o SonarQube se mostrou mais eficaz.\n\n")