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
        self.llm_data = self._normalize_llm_data(llm_data)
        self.sonarqube_data = self._normalize_sonarqube_data(sonarqube_data)
        self.output_dir = output_dir
        self.repo_name = repo_name
        os.makedirs(output_dir, exist_ok=True)

        self.categories_mapping = {
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
            "java:S1192": "Duplicate Code",
            "java:S112": "Exception Handling",
            "java:S1130": "Exception Handling",
            "java:S138": "Long Method",
            "java:S1448": "God Class",
            "java:S1200": "God Class",
            "java:S109": "Magic Numbers",
            "java:S3400": "Magic Numbers",
            "java:S1144": "Magic Numbers",
            "java:S1172": "Feature Envy",
            "java:S1104": "Data Class",
            "java:S1450": "Data Class"
        }

        self._extract_smells_and_files()

    def _normalize_llm_data(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                print("Erro ao fazer parse do JSON do LLM")
                return {}
        return data

    def _normalize_sonarqube_data(self, data):
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                print("Erro ao fazer parse do JSON do SonarQube")
                return {}
        return data

    def _extract_smells_and_files(self):
        self.llm_smells = []
        self.llm_files = set()
        if isinstance(self.llm_data, dict) and "smells_detectados" in self.llm_data:
            default_file = f"{self.repo_name}_file.java"
            self.llm_files.add(default_file)
            for smell_type in self.llm_data["smells_detectados"]:
                normalized_category = self.categories_mapping.get(smell_type, "Outros")
                confidence = "médio"
                if "confianca" in self.llm_data and smell_type in self.llm_data["confianca"]:
                    confidence = self.llm_data["confianca"][smell_type]
                description = self.llm_data.get("descricao", "")
                self.llm_smells.append({
                    "category": normalized_category,
                    "original_category": smell_type,
                    "file": default_file,
                    "lines": [],
                    "description": description,
                    "confidence": confidence
                })
        self.sonar_smells = []
        self.sonar_files = set()
        if isinstance(self.sonarqube_data, dict) and "issues" in self.sonarqube_data:
            for issue in self.sonarqube_data["issues"]:
                if issue.get("type") == "CODE_SMELL":
                    rule = issue.get("rule", "")
                    normalized_category = self.categories_mapping.get(rule, "Outros")
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
        self.all_files = self.llm_files.union(self.sonar_files)

    def question1_analysis(self):
        results = {}
        llm_count = len(self.llm_smells)
        sonar_count = len(self.sonar_smells)
        results["metrica_1_1"] = {
            "llm_total": llm_count,
            "sonarqube_total": sonar_count,
            "diferenca_absoluta": abs(llm_count - sonar_count),
            "relacao_percentual": (llm_count / sonar_count * 100) if sonar_count > 0 else float('inf')
        }
        llm_smells_por_arquivo = defaultdict(int)
        sonar_smells_por_arquivo = defaultdict(int)
        for smell in self.llm_smells:
            if smell["file"]:
                llm_smells_por_arquivo[smell["file"]] += 1
        for smell in self.sonar_smells:
            if smell["file"]:
                sonar_smells_por_arquivo[smell["file"]] += 1
        llm_media_por_arquivo = sum(llm_smells_por_arquivo.values()) / len(llm_smells_por_arquivo) if llm_smells_por_arquivo else 0
        sonar_media_por_arquivo = sum(sonar_smells_por_arquivo.values()) / len(sonar_smells_por_arquivo) if sonar_smells_por_arquivo else 0
        results["metrica_1_2"] = {
            "llm_media_por_arquivo": llm_media_por_arquivo,
            "sonarqube_media_por_arquivo": sonar_media_por_arquivo,
            "arquivos_com_smells_llm": len(llm_smells_por_arquivo),
            "arquivos_com_smells_sonarqube": len(sonar_smells_por_arquivo)
        }
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
        self._plot_question1_results(results)
        return results

    def _plot_question1_results(self, results):
        plt.figure(figsize=(10, 6))
        plt.bar(['LLM', 'SonarQube'],
                [results["metrica_1_1"]["llm_total"], results["metrica_1_1"]["sonarqube_total"]],
                color=['#3498db', '#e74c3c'])
        plt.title('Número Total de Code Smells Detectados')
        plt.ylabel('Quantidade de Code Smells')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/q1_total_smells.png")
        plt.close()
        plt.figure(figsize=(10, 6))
        plt.bar(['LLM', 'SonarQube'],
                [results["metrica_1_2"]["llm_media_por_arquivo"], results["metrica_1_2"]["sonarqube_media_por_arquivo"]],
                color=['#3498db', '#e74c3c'])
        plt.title('Média de Code Smells por Arquivo')
        plt.ylabel('Média de Code Smells')
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/q1_media_por_arquivo.png")
        plt.close()
        if results["metrica_1_3"]["arquivos_comuns"] > 0:
            diferencas = results["metrica_1_3"]["diferencas_por_arquivo"]
            arquivos = list(diferencas.keys())
            valores = list(diferencas.values())
            if len(arquivos) > 15:
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
        results = {}
        llm_por_categoria = defaultdict(int)
        sonar_por_categoria = defaultdict(int)
        for smell in self.llm_smells:
            llm_por_categoria[smell["category"]] += 1
        for smell in self.sonar_smells:
            sonar_por_categoria[smell["category"]] += 1
        categorias = set(llm_por_categoria.keys()).union(set(sonar_por_categoria.keys()))
        smells_comuns = 0
        total_smells = 0
        for cat in categorias:
            comuns = min(llm_por_categoria[cat], sonar_por_categoria[cat])
            smells_comuns += comuns
            total_smells += max(llm_por_categoria[cat], sonar_por_categoria[cat])
        taxa_similaridade = (smells_comuns / total_smells * 100) if total_smells > 0 else 0
        results["metrica_2_1"] = {
            "smells_comuns": smells_comuns,
            "total_smells_unicos": total_smells,
            "taxa_similaridade_percentual": taxa_similaridade
        }
        llm_exclusivos = sum(max(0, llm_por_categoria[cat] - sonar_por_categoria[cat]) for cat in categorias)
        sonar_exclusivos = sum(max(0, sonar_por_categoria[cat] - llm_por_categoria[cat]) for cat in categorias)
        results["metrica_2_2"] = {
            "llm_exclusivos": llm_exclusivos,
            "sonar_exclusivos": sonar_exclusivos,
            "taxa_exclusividade_llm": (llm_exclusivos / total_smells * 100) if total_smells > 0 else 0,
            "taxa_exclusividade_sonar": (sonar_exclusivos / total_smells * 100) if total_smells > 0 else 0
        }
        sobreposicao_por_categoria = {}
        for cat in categorias:
            total_cat = max(llm_por_categoria[cat], sonar_por_categoria[cat])
            comuns_cat = min(llm_por_categoria[cat], sonar_por_categoria[cat])
            sobreposicao_por_categoria[cat] = (comuns_cat / total_cat * 100) if total_cat > 0 else 0
        alta_sobreposicao = sum(1 for v in sobreposicao_por_categoria.values() if v >= 80)
        baixa_sobreposicao = sum(1 for v in sobreposicao_por_categoria.values() if v <= 20)
        results["metrica_2_3"] = {
            "categorias_alta_sobreposicao": alta_sobreposicao,
            "categorias_baixa_sobreposicao": baixa_sobreposicao,
            "total_categorias": len(sobreposicao_por_categoria),
            "sobreposicao_por_categoria": sobreposicao_por_categoria
        }
        self._plot_question2_results(results, list(categorias))
        return results

    def _plot_question2_results(self, results, categorias):
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
        results = {}
        categorias = set()
        for smell in self.llm_smells:
            categorias.add(smell["category"])
        for smell in self.sonar_smells:
            categorias.add(smell["category"])
        categorias = sorted(list(categorias))
        llm_por_categoria = defaultdict(int)
        sonar_por_categoria = defaultdict(int)
        for smell in self.llm_smells:
            llm_por_categoria[smell["category"]] += 1
        for smell in self.sonar_smells:
            sonar_por_categoria[smell["category"]] += 1
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
        simultaneos_por_categoria = {}
        exclusivos_llm_por_categoria = {}
        exclusivos_sonar_por_categoria = {}
        percentual_simultaneos_por_categoria = {}
        percentual_exclusivos_llm_por_categoria = {}
        percentual_exclusivos_sonar_por_categoria = {}
        for categoria in categorias:
            llm_count = llm_por_categoria[categoria]
            sonar_count = sonar_por_categoria[categoria]
            simultaneos = min(llm_count, sonar_count)
            exclusivos_llm = max(0, llm_count - sonar_count)
            exclusivos_sonar = max(0, sonar_count - llm_count)
            total_cat = max(llm_count, sonar_count)
            simultaneos_por_categoria[categoria] = simultaneos
            exclusivos_llm_por_categoria[categoria] = exclusivos_llm
            exclusivos_sonar_por_categoria[categoria] = exclusivos_sonar
            percentual_simultaneos_por_categoria[categoria] = (simultaneos / total_cat * 100) if total_cat > 0 else 0
            percentual_exclusivos_llm_por_categoria[categoria] = (exclusivos_llm / total_cat * 100) if total_cat > 0 else 0
            percentual_exclusivos_sonar_por_categoria[categoria] = (exclusivos_sonar / total_cat * 100) if total_cat > 0 else 0
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
        self._plot_question3_results(results, categorias)
        return results, categorias

    def _plot_question3_results(self, results, categorias):
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
        plt.figure(figsize=(12, 8))
        simultaneos = [results["metrica_3_2"]["percentual_simultaneos_por_categoria"].get(c, 0) for c in categorias]
        exclusivos_llm = [results["metrica_3_3"]["percentual_exclusivos_llm_por_categoria"].get(c, 0) for c in categorias]
        exclusivos_sonar = [results["metrica_3_3"]["percentual_exclusivos_sonar_por_categoria"].get(c, 0) for c in categorias]
        x = np.arange(len(categorias))
        width = 0.8
        exc_llm_arr = np.array(exclusivos_llm)
        sim_arr = np.array(simultaneos)
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
        plt.figure(figsize=(12, 8))
        data = []
        for c in categorias:
            data.append([
                results["metrica_3_1"]["llm_por_categoria"].get(c, 0),
                results["metrica_3_1"]["sonarqube_por_categoria"].get(c, 0),
                results["metrica_3_2"]["simultaneos_por_categoria"].get(c, 0)
            ])
        data_array = np.array(data)
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
        print("Gerando análises para as 3 perguntas do GQM atualizado...")
        q1_results = self.question1_analysis()
        q2_results = self.question2_analysis()
        q3_results, categorias = self.question3_analysis()
        results = {
            "repositorio": self.repo_name,
            "question1": q1_results,
            "question2": q2_results,
            "question3": q3_results,
            "categorias": list(categorias)
        }
        with open(f"{self.output_dir}/resultados_gqm.json", 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Relatório completo gerado com sucesso em {self.output_dir}")
        self._generate_markdown_report(results, categorias)
        return results

    def _generate_markdown_report(self, results, categorias):
        with open(f"{self.output_dir}/relatorio_gqm.md", 'w') as f:
            f.write("# Relatório GQM: Comparação entre LLM e SonarQube na Detecção de Code Smells\n\n")
            f.write(f"Repositório analisado: **{self.repo_name}**\n\n")
            f.write("## Questão 1: Qual das duas abordagens detecta mais code smells clássicos?\n\n")
            f.write("### Métrica 1.1: Número total de code smells detectados\n\n")
            f.write("| Abordagem | Quantidade de Smells |\n")
            f.write("|-----------|----------------------|\n")
            f.write(f"| LLM | {results['question1']['metrica_1_1']['llm_total']} |\n")
            f.write(f"| SonarQube | {results['question1']['metrica_1_1']['sonarqube_total']} |\n")
            f.write(f"| Diferença absoluta | {results['question1']['metrica_1_1']['diferenca_absoluta']} |\n")
            f.write(f"| Relação percentual (LLM/SonarQube) | {results['question1']['metrica_1_1']['relacao_percentual']:.2f}% |\n\n")
            f.write("### Métrica 1.2: Média de code smells detectados por arquivo\n\n")
            f.write("| Abordagem | Média de Smells por Arquivo | Arquivos com Smells |\n")
            f.write("|-----------|------------------------------|---------------------|\n")
            f.write(f"| LLM | {results['question1']['metrica_1_2']['llm_media_por_arquivo']:.2f} | {results['question1']['metrica_1_2']['arquivos_com_smells_llm']} |\n")
            f.write(f"| SonarQube | {results['question1']['metrica_1_2']['sonarqube_media_por_arquivo']:.2f} | {results['question1']['metrica_1_2']['arquivos_com_smells_sonarqube']} |\n\n")
            f.write("### Métrica 1.3: Diferença média de detecção por arquivo\n\n")
            f.write(f"- Diferença média por arquivo: **{results['question1']['metrica_1_3']['diferenca_media_por_arquivo']:.2f}**\n")
            f.write(f"- Número de arquivos comuns analisados: **{results['question1']['metrica_1_3']['arquivos_comuns']}**\n\n")
            f.write("![Total de Code Smells](./q1_total_smells.png)\n\n")
            f.write("![Média por Arquivo](./q1_media_por_arquivo.png)\n\n")
            if results['question1']['metrica_1_3']['arquivos_comuns'] > 0:
                f.write("![Diferença por Arquivo](./q1_diferenca_por_arquivo.png)\n\n")
            f.write("## Questão 2: As duas abordagens convergem ou divergem nos resultados?\n\n")
            f.write("### Métrica 2.1: Porcentagem de smells detectados simultaneamente\n\n")
            f.write("| Métrica | Valor |\n")
            f.write("|---------|-------|\n")
            f.write(f"| Smells detectados por ambas abordagens | {results['question2']['metrica_2_1']['smells_comuns']} |\n")
            f.write(f"| Total de smells únicos (união) | {results['question2']['metrica_2_1']['total_smells_unicos']} |\n")
            f.write(f"| Taxa de similaridade | {results['question2']['metrica_2_1']['taxa_similaridade_percentual']:.2f}% |\n\n")
            f.write("### Métrica 2.2: Porcentagem de smells exclusivos\n\n")
            f.write("| Métrica | Valor |\n")
            f.write("|---------|-------|\n")
            f.write(f"| Smells exclusivos LLM | {results['question2']['metrica_2_2']['llm_exclusivos']} |\n")
            f.write(f"| Smells exclusivos SonarQube | {results['question2']['metrica_2_2']['sonar_exclusivos']} |\n")
            f.write(f"| Taxa de exclusividade LLM | {results['question2']['metrica_2_2']['taxa_exclusividade_llm']:.2f}% |\n")
            f.write(f"| Taxa de exclusividade SonarQube | {results['question2']['metrica_2_2']['taxa_exclusividade_sonar']:.2f}% |\n\n")
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
            f.write("## Questão 3: Existem categorias de smells mais detectadas por cada abordagem?\n\n")
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
            f.write("### Métrica 3.2: Porcentagem de smells simultâneos por categoria\n\n")
            f.write("| Categoria | Número de Smells Simultâneos | % de Simultaneidade |\n")
            f.write("|-----------|------------------------------|--------------------|\n")
            for c in categorias:
                count = results['question3']['metrica_3_2']['simultaneos_por_categoria'].get(c, 0)
                percent = results['question3']['metrica_3_2']['percentual_simultaneos_por_categoria'].get(c, 0)
                f.write(f"| {c} | {count} | {percent:.2f}% |\n")
            f.write("\n")
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
            f.write("## Conclusões\n\n")
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
            f.write("### Questão 3: Existem categorias de smells mais detectadas por cada abordagem?\n\n")
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

if __name__ == "__main__":
    # Ajuste os caminhos conforme necessário
    llm_path = "../data/llm/llm_resultado.json"
    sonar_path = "../data/sonarqube/sonarqube_resultado.json"
    output_dir = "../results"
    repo_name = ".repo"

    # Carregar dados
    with open(llm_path, encoding="utf-8") as f:
        llm_data = json.load(f)
    with open(sonar_path, encoding="utf-8") as f:
        sonar_data = json.load(f)

    # Instanciar e rodar análise
    comparator = CodeSmellComparator(llm_data, sonar_data, output_dir=output_dir, repo_name=repo_name)
    comparator.generate_complete_report()