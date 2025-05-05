import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from sklearn.metrics import cohen_kappa_score

class CodeSmellComparator:
    """
    Classe para comparar resultados de detecção de code smells entre LLM e SonarQube,
    seguindo o modelo GQM (Goal-Question-Metric).
    """
    
    def __init__(self, llm_data, sonarqube_data, output_dir='./results'):
        """
        Inicializa o comparador com os dados das duas abordagens.
        
        Args:
            llm_data: Dados de code smells detectados por LLMs
            sonarqube_data: Dados de code smells detectados por SonarQube
            output_dir: Diretório para salvar resultados e gráficos
        """
        self.llm_data = self._normalize_llm_data(llm_data)
        self.sonarqube_data = self._normalize_sonarqube_data(sonarqube_data)
        self.output_dir = output_dir
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
            for smell_type in self.llm_data["smells_detectados"]:
                # Normalizar categoria
                normalized_category = self.categories_mapping.get(smell_type, "Outros")
                
                # Extrair localização
                location = self.llm_data["localizacao"].get(smell_type, "")
                file_name = None
                lines = []
                
                if ":" in location:
                    file_part, line_part = location.split(":", 1)
                    file_name = file_part
                    
                    if "-" in line_part:
                        try:
                            start, end = map(int, line_part.split("-"))
                            lines = list(range(start, end + 1))
                        except ValueError:
                            lines = []
                
                if file_name:
                    self.llm_files.add(file_name)
                
                self.llm_smells.append({
                    "category": normalized_category,
                    "original_category": smell_type,
                    "file": file_name,
                    "lines": lines,
                    "description": self.llm_data["descricao"].get(smell_type, ""),
                    "confidence": self.llm_data["confianca"].get(smell_type, "médio")
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
                    
                    # Extrair linhas
                    lines = []
                    if "line" in issue:
                        lines = [issue["line"]]
                    elif "textRange" in issue:
                        start_line = issue["textRange"].get("startLine")
                        end_line = issue["textRange"].get("endLine")
                        if start_line and end_line:
                            lines = list(range(start_line, end_line + 1))
                    
                    if file_name:
                        self.sonar_files.add(file_name)
                    
                    self.sonar_smells.append({
                        "category": normalized_category,
                        "original_category": rule,
                        "file": file_name,
                        "lines": lines,
                        "message": issue.get("message", ""),
                        "severity": issue.get("severity", "")
                    })
        
        # União de todos os arquivos relevantes
        self.all_files = self.llm_files.union(self.sonar_files)
        
    def analyze_pergunta1(self):
        """
        Análise da Pergunta 1: Qual abordagem detecta mais code smells clássicos?
        Retorna métricas: Total de Smells, Taxa de Similaridade e Taxa de Divergência
        """
        results = {}
        
        # M1: Total de Smells Detectados
        llm_count = len(self.llm_smells)
        sonar_count = len(self.sonar_smells)
        
        results["m1_total_smells"] = {
            "llm": llm_count,
            "sonarqube": sonar_count
        }
        
        # Para M2 e M3, precisamos identificar smells comuns e exclusivos
        # Criamos fingerprints para cada smell para facilitar a comparação
        llm_fingerprints = set()
        sonar_fingerprints = set()
        
        for smell in self.llm_smells:
            if smell["file"] and smell["lines"]:
                for line in smell["lines"]:
                    llm_fingerprints.add(f"{smell['file']}:{line}:{smell['category']}")
            elif smell["file"]:
                llm_fingerprints.add(f"{smell['file']}:{smell['category']}")
        
        for smell in self.sonar_smells:
            if smell["file"] and smell["lines"]:
                for line in smell["lines"]:
                    sonar_fingerprints.add(f"{smell['file']}:{line}:{smell['category']}")
            elif smell["file"]:
                sonar_fingerprints.add(f"{smell['file']}:{smell['category']}")
        
        # Calcular intersecção e união
        intersecao = llm_fingerprints.intersection(sonar_fingerprints)
        uniao = llm_fingerprints.union(sonar_fingerprints)
        
        # M2: Taxa de Similaridade (overlap)
        if len(uniao) > 0:
            taxa_similaridade = (len(intersecao) / len(uniao)) * 100
        else:
            taxa_similaridade = 0
        
        results["m2_similaridade"] = {
            "smells_comuns": len(intersecao),
            "total_smells_unicos": len(uniao),
            "taxa_similaridade": taxa_similaridade
        }
        
        # M3: Taxa de Divergência
        llm_exclusivos = llm_fingerprints - sonar_fingerprints
        sonar_exclusivos = sonar_fingerprints - llm_fingerprints
        
        if len(uniao) > 0:
            taxa_divergencia_llm = (len(llm_exclusivos) / len(uniao)) * 100
            taxa_divergencia_sonar = (len(sonar_exclusivos) / len(uniao)) * 100
        else:
            taxa_divergencia_llm = 0
            taxa_divergencia_sonar = 0
        
        results["m3_divergencia"] = {
            "llm_exclusivos": len(llm_exclusivos),
            "sonar_exclusivos": len(sonar_exclusivos),
            "taxa_divergencia_llm": taxa_divergencia_llm,
            "taxa_divergencia_sonar": taxa_divergencia_sonar
        }
        
        # Gerar gráfico para Total de Smells
        plt.figure(figsize=(10, 6))
        plt.bar(['LLM', 'SonarQube'], [llm_count, sonar_count], color=['#3498db', '#e74c3c'])
        plt.title('Total de Code Smells Detectados')
        plt.ylabel('Número de Code Smells')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/p1_total_smells.png")
        plt.close()
        
        # Gerar gráfico para Similaridade/Divergência
        plt.figure(figsize=(10, 6))
        plt.bar(['Exclusivos LLM', 'Em Comum', 'Exclusivos SonarQube'], 
                [len(llm_exclusivos), len(intersecao), len(sonar_exclusivos)],
                color=['#3498db', '#2ecc71', '#e74c3c'])
        plt.title('Distribuição de Code Smells entre as Ferramentas')
        plt.ylabel('Número de Code Smells')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/p1_similaridade_divergencia.png")
        plt.close()
        
        return results
    
    def analyze_pergunta2(self):
        """
        Análise da Pergunta 2: Qual abordagem apresenta maior amplitude de cobertura?
        Retorna métricas: Total de Arquivos Relevantes, Cobertura por Abordagem, 
        Média de Categorias por Arquivo
        """
        results = {}
        
        # M1: Total de Arquivos Relevantes
        total_arquivos = len(self.all_files)
        
        results["m1_arquivos_relevantes"] = {
            "total": total_arquivos,
            "arquivos": list(self.all_files)
        }
        
        # M2: Cobertura por Abordagem
        cobertura_llm = len(self.llm_files)
        cobertura_sonar = len(self.sonar_files)
        
        if total_arquivos > 0:
            perc_cobertura_llm = (cobertura_llm / total_arquivos) * 100
            perc_cobertura_sonar = (cobertura_sonar / total_arquivos) * 100
        else:
            perc_cobertura_llm = 0
            perc_cobertura_sonar = 0
        
        results["m2_cobertura"] = {
            "llm_arquivos": cobertura_llm,
            "sonar_arquivos": cobertura_sonar,
            "perc_cobertura_llm": perc_cobertura_llm,
            "perc_cobertura_sonar": perc_cobertura_sonar
        }
        
        # M3: Média de Categorias por Arquivo
        categorias_por_arquivo_llm = defaultdict(set)
        categorias_por_arquivo_sonar = defaultdict(set)
        
        for smell in self.llm_smells:
            if smell["file"]:
                categorias_por_arquivo_llm[smell["file"]].add(smell["category"])
                
        for smell in self.sonar_smells:
            if smell["file"]:
                categorias_por_arquivo_sonar[smell["file"]].add(smell["category"])
        
        # Calcular médias
        media_categorias_llm = 0
        media_categorias_sonar = 0
        
        if len(categorias_por_arquivo_sonar) > 0:
            media_categorias_sonar = sum(len(cats) for cats in categorias_por_arquivo_sonar.values()) / len(categorias_por_arquivo_sonar)
        
        results["m3_categorias_por_arquivo"] = {
            "media_llm": media_categorias_llm,
            "media_sonar": media_categorias_sonar,
            "detalhes_llm": {file: list(cats) for file, cats in categorias_por_arquivo_llm.items()},
            "detalhes_sonar": {file: list(cats) for file, cats in categorias_por_arquivo_sonar.items()}
        }
        
        # Gerar gráfico para Cobertura
        plt.figure(figsize=(10, 6))
        plt.bar(['LLM', 'SonarQube'], [perc_cobertura_llm, perc_cobertura_sonar], color=['#3498db', '#e74c3c'])
        plt.title('Cobertura de Arquivos Relevantes (%)')
        plt.ylabel('Porcentagem de Cobertura')
        plt.ylim(0, 100)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/p2_cobertura.png")
        plt.close()
        
        # Gerar gráfico para Média de Categorias
        plt.figure(figsize=(10, 6))
        plt.bar(['LLM', 'SonarQube'], [media_categorias_llm, media_categorias_sonar], color=['#3498db', '#e74c3c'])
        plt.title('Média de Categorias de Code Smells por Arquivo')
        plt.ylabel('Número médio de categorias')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/p2_media_categorias.png")
        plt.close()
        
        return results
    
    def analyze_pergunta3(self):
        """
        Análise da Pergunta 3: Qual o desempenho e grau de concordância entre LLMs e SonarQube, 
        por categoria de code smell?
        Retorna métricas: Precisão/Recall/F1, Kappa de Cohen, Exclusividade de Detecção
        """
        # Definir categorias principais para análise
        categorias = [
            "Long Method", 
            "God Class", 
            "Duplicate Code",
            "Feature Envy", 
            "Data Class",
            "Magic Numbers",
            "Exception Handling",
            "Outros"
        ]
        
        results = {cat: {} for cat in categorias}
        
        # Para cada arquivo e linha, rastrear qual ferramenta detectou qual categoria
        deteccoes = defaultdict(lambda: {"llm": set(), "sonar": set()})
        
        for smell in self.llm_smells:
            if smell["file"] and smell["lines"]:
                for line in smell["lines"]:
                    key = f"{smell['file']}:{line}"
                    deteccoes[key]["llm"].add(smell["category"])
            elif smell["file"]:
                key = smell["file"]
                deteccoes[key]["llm"].add(smell["category"])
        
        for smell in self.sonar_smells:
            if smell["file"] and smell["lines"]:
                for line in smell["lines"]:
                    key = f"{smell['file']}:{line}"
                    deteccoes[key]["sonar"].add(smell["category"])
            elif smell["file"]:
                key = smell["file"]
                deteccoes[key]["sonar"].add(smell["category"])
        
        # Análise por categoria
        precision_values = []
        recall_values = []
        f1_values = []
        kappa_values = []
        exclusivo_llm_values = []
        exclusivo_sonar_values = []
        
        for categoria in categorias:
            # Para cálculo de Precision, Recall e F1
            tp = 0  # True Positives - ambos detectaram
            fp = 0  # False Positives - LLM detectou, SonarQube não
            fn = 0  # False Negatives - SonarQube detectou, LLM não
            
            # Para Cohen's Kappa
            llm_detectou = []  # Detecção pelo LLM (1=sim, 0=não)
            sonar_detectou = []  # Detecção pelo SonarQube (1=sim, 0=não)
            
            # Para exclusividade
            exclusivo_llm = 0
            exclusivo_sonar = 0
            
            for key, ferramentas in deteccoes.items():
                llm_tem = categoria in ferramentas["llm"]
                sonar_tem = categoria in ferramentas["sonar"]
                
                # Incrementar estatísticas
                if llm_tem and sonar_tem:
                    tp += 1
                elif llm_tem and not sonar_tem:
                    fp += 1
                    exclusivo_llm += 1
                elif not llm_tem and sonar_tem:
                    fn += 1
                    exclusivo_sonar += 1
                
                llm_detectou.append(1 if llm_tem else 0)
                sonar_detectou.append(1 if sonar_tem else 0)
            
            # Calcular métricas
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            # Calcular Kappa de Cohen
            kappa = cohen_kappa_score(llm_detectou, sonar_detectou) if (len(llm_detectou) > 0 and len(set(llm_detectou+sonar_detectou)) > 1) else 0
            
            # Armazenar resultados
            results[categoria] = {
                "m1_precision_recall_f1": {
                    "true_positives": tp,
                    "false_positives": fp,
                    "false_negatives": fn,
                    "precision": precision,
                    "recall": recall,
                    "f1": f1
                },
                "m2_kappa": kappa,
                "m3_exclusividade": {
                    "exclusivo_llm": exclusivo_llm,
                    "exclusivo_sonar": exclusivo_sonar,
                    "total": tp + fp + fn
                }
            }
            
            # Guardar valores para gráficos
            precision_values.append(precision)
            recall_values.append(recall)
            f1_values.append(f1)
            kappa_values.append(kappa)
            exclusivo_llm_values.append(exclusivo_llm)
            exclusivo_sonar_values.append(exclusivo_sonar)
        
        # Gerar gráficos
        # 1. Métricas por categoria
        plt.figure(figsize=(12, 8))
        x = np.arange(len(categorias))
        width = 0.2
        
        plt.bar(x - width*1.5, precision_values, width, label='Precision', color='#3498db')
        plt.bar(x - width/2, recall_values, width, label='Recall', color='#e74c3c')
        plt.bar(x + width/2, f1_values, width, label='F1-Score', color='#2ecc71')
        plt.bar(x + width*1.5, kappa_values, width, label='Cohen\'s Kappa', color='#f39c12')
        
        plt.xlabel('Categoria de Code Smell')
        plt.ylabel('Valor')
        plt.title('Métricas de Desempenho por Categoria')
        plt.xticks(x, categorias, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/p3_metricas.png")
        plt.close()
        
        # 2. Exclusividade por categoria
        plt.figure(figsize=(12, 8))
        
        bottom_vals = np.zeros(len(categorias))
        
        plt.bar(categorias, exclusivo_llm_values, label='Exclusivos LLM', color='#3498db')
        plt.bar(categorias, exclusivo_sonar_values, bottom=exclusivo_llm_values, 
                label='Exclusivos SonarQube', color='#e74c3c')
        
        plt.xlabel('Categoria de Code Smell')
        plt.ylabel('Número de Smells Exclusivos')
        plt.title('Exclusividade de Detecção por Categoria')
        plt.xticks(rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/p3_exclusividade.png")
        plt.close()
        
        return results
    
    def generate_complete_report(self):
        """
        Gera um relatório completo com todas as análises
        """
        # Executar todas as análises
        print("Gerando análises para as 3 perguntas do GQM...")
        
        p1_results = self.analyze_pergunta1()
        p2_results = self.analyze_pergunta2()
        p3_results = self.analyze_pergunta3()
        
        # Consolidar resultados
        results = {
            "pergunta1": p1_results,
            "pergunta2": p2_results,
            "pergunta3": p3_results
        }
        
        # Salvar resultados em JSON
        with open(f"{self.output_dir}/resultados_gqm.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Relatório completo gerado com sucesso em {self.output_dir}")
        
        # Gerar tabelas para o relatório em formato markdown
        self._generate_markdown_report(results)
        
        return results
    
    def _generate_markdown_report(self, results):
        """
        Gera um relatório em formato markdown com os resultados
        """
        with open(f"{self.output_dir}/relatorio_gqm.md", 'w') as f:
            f.write("# Relatório GQM: Comparação entre LLM e SonarQube na Detecção de Code Smells\n\n")
            
            # Pergunta 1
            f.write("## Pergunta 1: Qual abordagem detecta mais code smells clássicos?\n\n")
            
            # M1: Total de Smells
            f.write("### M1: Total de Smells Detectados\n\n")
            f.write("| Ferramenta | Quantidade de Smells |\n")
            f.write("|------------|----------------------|\n")
            f.write(f"| LLM | {results['pergunta1']['m1_total_smells']['llm']} |\n")
            f.write(f"| SonarQube | {results['pergunta1']['m1_total_smells']['sonarqube']} |\n\n")
            
            # M2: Taxa de Similaridade
            f.write("### M2: Taxa de Similaridade (overlap)\n\n")
            f.write("| Métrica | Valor |\n")
            f.write("|---------|-------|\n")
            f.write(f"| Smells em comum | {results['pergunta1']['m2_similaridade']['smells_comuns']} |\n")
            f.write(f"| Total de smells únicos | {results['pergunta1']['m2_similaridade']['total_smells_unicos']} |\n")
            f.write(f"| Taxa de similaridade | {results['pergunta1']['m2_similaridade']['taxa_similaridade']:.2f}% |\n\n")
            
            # M3: Taxa de Divergência
            f.write("### M3: Taxa de Divergência\n\n")
            f.write("| Métrica | Valor |\n")
            f.write("|---------|-------|\n")
            f.write(f"| Smells exclusivos LLM | {results['pergunta1']['m3_divergencia']['llm_exclusivos']} |\n")
            f.write(f"| Smells exclusivos SonarQube | {results['pergunta1']['m3_divergencia']['sonar_exclusivos']} |\n")
            f.write(f"| Taxa de divergência LLM | {results['pergunta1']['m3_divergencia']['taxa_divergencia_llm']:.2f}% |\n")
            f.write(f"| Taxa de divergência SonarQube | {results['pergunta1']['m3_divergencia']['taxa_divergencia_sonar']:.2f}% |\n\n")
            
            f.write("![Total de Smells](./p1_total_smells.png)\n\n")
            f.write("![Similaridade e Divergência](./p1_similaridade_divergencia.png)\n\n")
            
            # Pergunta 2
            f.write("## Pergunta 2: Qual abordagem apresenta maior amplitude de cobertura?\n\n")
            
            # M1: Total de Arquivos Relevantes
            f.write("### M1: Total de Arquivos Relevantes\n\n")
            f.write(f"Total de arquivos relevantes: **{results['pergunta2']['m1_arquivos_relevantes']['total']}**\n\n")
            
            # M2: Cobertura por Abordagem
            f.write("### M2: Cobertura por Abordagem\n\n")
            f.write("| Ferramenta | Arquivos Cobertos | Porcentagem |\n")
            f.write("|------------|-------------------|-------------|\n")
            f.write(f"| LLM | {results['pergunta2']['m2_cobertura']['llm_arquivos']} | {results['pergunta2']['m2_cobertura']['perc_cobertura_llm']:.2f}% |\n")
            f.write(f"| SonarQube | {results['pergunta2']['m2_cobertura']['sonar_arquivos']} | {results['pergunta2']['m2_cobertura']['perc_cobertura_sonar']:.2f}% |\n\n")
            
            # M3: Média de Categorias por Arquivo
            f.write("### M3: Média de Categorias por Arquivo\n\n")
            f.write("| Ferramenta | Média de Categorias por Arquivo |\n")
            f.write("|------------|----------------------------------|\n")
            f.write(f"| LLM | {results['pergunta2']['m3_categorias_por_arquivo']['media_llm']:.2f} |\n")
            f.write(f"| SonarQube | {results['pergunta2']['m3_categorias_por_arquivo']['media_sonar']:.2f} |\n\n")
            
            f.write("![Cobertura de Arquivos](./p2_cobertura.png)\n\n")
            f.write("![Média de Categorias](./p2_media_categorias.png)\n\n")
            
            # Pergunta 3
            f.write("## Pergunta 3: Qual o desempenho e grau de concordância por categoria?\n\n")
            
            # M1: Precision, Recall e F1
            f.write("### M1: Precisão, Recall e F1 por Categoria\n\n")
            f.write("| Categoria | Precision | Recall | F1 |\n")
            f.write("|-----------|-----------|--------|----|\n")
            
            for categoria in results['pergunta3']:
                precision = results['pergunta3'][categoria]['m1_precision_recall_f1']['precision']
                recall = results['pergunta3'][categoria]['m1_precision_recall_f1']['recall']
                f1 = results['pergunta3'][categoria]['m1_precision_recall_f1']['f1']
                
                f.write(f"| {categoria} | {precision:.4f} | {recall:.4f} | {f1:.4f} |\n")
            
            f.write("\n")
            
            # M2: Kappa de Cohen por Categoria
            f.write("### M2: Kappa de Cohen por Categoria\n\n")
            f.write("| Categoria | Kappa de Cohen |\n")
            f.write("|-----------|---------------|\n")
            
            for categoria in results['pergunta3']:
                kappa = results['pergunta3'][categoria]['m2_kappa']
                f.write(f"| {categoria} | {kappa:.4f} |\n")
            
            f.write("\n")
            
            # M3: Exclusividade de Detecção por Categoria
            f.write("### M3: Exclusividade de Detecção por Categoria\n\n")
            f.write("| Categoria | Exclusivos LLM | Exclusivos SonarQube | Total |\n")
            f.write("|-----------|----------------|----------------------|-------|\n")
            
            for categoria in results['pergunta3']:
                exclusivo_llm = results['pergunta3'][categoria]['m3_exclusividade']['exclusivo_llm']
                exclusivo_sonar = results['pergunta3'][categoria]['m3_exclusividade']['exclusivo_sonar']
                total = results['pergunta3'][categoria]['m3_exclusividade']['total']
                
                f.write(f"| {categoria} | {exclusivo_llm} | {exclusivo_sonar} | {total} |\n")
            
            f.write("\n")
            
            f.write("![Métricas por Categoria](./p3_metricas.png)\n\n")
            f.write("![Exclusividade por Categoria](./p3_exclusividade.png)\n\n")
            
            # Conclusões
            f.write("## Conclusões\n\n")
            
            # Pergunta 1 - Conclusão
            llm_count = results['pergunta1']['m1_total_smells']['llm']
            sonar_count = results['pergunta1']['m1_total_smells']['sonarqube']
            
            f.write("### Pergunta 1: Qual abordagem detecta mais code smells clássicos?\n\n")
            if llm_count > sonar_count:
                f.write(f"A abordagem LLM detectou mais code smells ({llm_count}) em comparação com o SonarQube ({sonar_count}). ")
            elif sonar_count > llm_count:
                f.write(f"O SonarQube detectou mais code smells ({sonar_count}) em comparação com a abordagem LLM ({llm_count}). ")
            else:
                f.write(f"Ambas as abordagens detectaram o mesmo número de code smells ({llm_count}). ")
                
            f.write(f"A taxa de similaridade entre as abordagens foi de {results['pergunta1']['m2_similaridade']['taxa_similaridade']:.2f}%, ")
            f.write(f"indicando um grau de {('baixo' if results['pergunta1']['m2_similaridade']['taxa_similaridade'] < 30 else 'médio' if results['pergunta1']['m2_similaridade']['taxa_similaridade'] < 70 else 'alto')} ")
            f.write("de concordância entre as ferramentas.\n\n")
            
            # Pergunta 2 - Conclusão
            perc_llm = results['pergunta2']['m2_cobertura']['perc_cobertura_llm']
            perc_sonar = results['pergunta2']['m2_cobertura']['perc_cobertura_sonar']
            
            f.write("### Pergunta 2: Qual abordagem apresenta maior amplitude de cobertura?\n\n")
            if perc_llm > perc_sonar:
                f.write(f"A abordagem LLM apresentou maior amplitude de cobertura, analisando {perc_llm:.2f}% dos arquivos relevantes, ")
                f.write(f"enquanto o SonarQube cobriu {perc_sonar:.2f}%. ")
            elif perc_sonar > perc_llm:
                f.write(f"O SonarQube apresentou maior amplitude de cobertura, analisando {perc_sonar:.2f}% dos arquivos relevantes, ")
                f.write(f"enquanto a abordagem LLM cobriu {perc_llm:.2f}%. ")
            else:
                f.write(f"Ambas as abordagens apresentaram a mesma amplitude de cobertura, analisando {perc_llm:.2f}% dos arquivos relevantes. ")
            
            media_llm = results['pergunta2']['m3_categorias_por_arquivo']['media_llm']
            media_sonar = results['pergunta2']['m3_categorias_por_arquivo']['media_sonar']
            
            f.write(f"Em termos de diversidade, a LLM detectou em média {media_llm:.2f} categorias diferentes de smells por arquivo, ")
            f.write(f"enquanto o SonarQube detectou {media_sonar:.2f} categorias.\n\n")
            
            # Pergunta 3 - Conclusão
            f.write("### Pergunta 3: Qual o desempenho e grau de concordância por categoria?\n\n")
            
            # Encontrar categoria com melhor F1 para cada abordagem
            melhor_f1 = 0
            melhor_categoria_f1 = "Nenhuma"
            
            melhor_kappa = -1
            melhor_categoria_kappa = "Nenhuma"
            
            for categoria, dados in results['pergunta3'].items():
                f1 = dados['m1_precision_recall_f1']['f1']
                kappa = dados['m2_kappa']
                
                if f1 > melhor_f1:
                    melhor_f1 = f1
                    melhor_categoria_f1 = categoria
                    
                if kappa > melhor_kappa:
                    melhor_kappa = kappa
                    melhor_categoria_kappa = categoria
            
            f.write(f"A categoria com melhor desempenho (F1-Score) foi **{melhor_categoria_f1}** com F1 de {melhor_f1:.4f}. ")
            f.write(f"O maior grau de concordância (Kappa de Cohen) foi observado na categoria **{melhor_categoria_kappa}** ")
            f.write(f"com valor de {melhor_kappa:.4f}, indicando um nível de concordância ")
            
            if melhor_kappa < 0:
                f.write("menor que o esperado por chance.\n\n")
            elif melhor_kappa < 0.2:
                f.write("leve.\n\n")
            elif melhor_kappa < 0.4:
                f.write("razoável.\n\n")
            elif melhor_kappa < 0.6:
                f.write("moderado.\n\n")
            elif melhor_kappa < 0.8:
                f.write("substancial.\n\n")
            else:
                f.write("quase perfeito.\n\n")
          