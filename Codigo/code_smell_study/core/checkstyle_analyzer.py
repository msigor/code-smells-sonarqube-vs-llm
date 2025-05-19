"""
Módulo para analisar repositórios Java usando CheckStyle.
"""

import os
import json
import subprocess
import logging
import argparse
import xml.etree.ElementTree as ET
from tqdm import tqdm
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("checkstyle_analyzer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CheckStyleAnalyzer:
    """Classe para analisar projetos Java usando CheckStyle."""
    
    def __init__(self, config_path=None, output_dir=None, checkstyle_jar=None):
        """
        Inicializa o analisador CheckStyle.
        
        Args:
            config_path: Caminho para o arquivo de configuração do CheckStyle
            output_dir: Diretório onde serão salvos os resultados
            checkstyle_jar: Caminho para o JAR do CheckStyle
        """
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Definir caminhos
        self.config_path = config_path or os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config", "checkstyle-config.xml"
        ))
        
        self.output_dir = output_dir or os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "checkstyle"
        ))
        
        # Caminho para o JAR do CheckStyle (se fornecido)
        self.checkstyle_jar = checkstyle_jar
        
        # Garantir que o diretório de saída existe
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Verificar se o CheckStyle está instalado/disponível
        if not self._check_checkstyle():
            raise RuntimeError("CheckStyle não encontrado ou não está funcionando corretamente")
        
        # Verificar se o arquivo de configuração existe
        if not os.path.exists(self.config_path):
            logger.error(f"Arquivo de configuração do CheckStyle não encontrado: {self.config_path}")
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")
    
    def _check_checkstyle(self):
        """Verifica se o CheckStyle está instalado e acessível."""
        # Se já temos o caminho para o JAR, verificar se ele existe
        if self.checkstyle_jar and os.path.exists(self.checkstyle_jar):
            logger.info(f"Usando JAR do CheckStyle especificado: {self.checkstyle_jar}")
            return self._test_checkstyle_jar(self.checkstyle_jar)
        
        # Procurar o JAR do CheckStyle em vários locais possíveis
        possible_jar_locations = [
            "checkstyle.jar",  # No PATH atual
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "checkstyle.jar"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "checkstyle.jar"),
            os.path.join(os.getcwd(), "checkstyle.jar"),
            os.path.join(os.getcwd(), "config", "checkstyle.jar")
        ]
        
        for jar_path in possible_jar_locations:
            if os.path.exists(jar_path):
                logger.info(f"CheckStyle JAR encontrado em: {jar_path}")
                self.checkstyle_jar = jar_path
                return self._test_checkstyle_jar(jar_path)
        
        # Se não encontrou em nenhum dos locais, baixar automaticamente
        logger.warning("CheckStyle não encontrado nos locais padrão. Baixando automaticamente...")
        return self._download_checkstyle()
    
    def _test_checkstyle_jar(self, jar_path):
        """Testa se o arquivo JAR do CheckStyle funciona."""
        try:
            # Criar um arquivo Java de teste simples
            test_file = os.path.join(os.getcwd(), "test_checkstyle.java")
            with open(test_file, 'w') as f:
                f.write("public class test_checkstyle { public void method() { } }")
            
            # Testar o CheckStyle com o arquivo Java
            cmd = [
                "java", "-jar", jar_path,
                "-c", self.config_path,
                test_file
            ]
            
            logger.info(f"Testando CheckStyle com comando: {' '.join(cmd)}")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            # Remover o arquivo de teste
            try:
                os.remove(test_file)
            except:
                pass
            
            # Se o retorno for 0, o CheckStyle está funcionando corretamente
            if process.returncode == 0:
                logger.info("CheckStyle funciona corretamente")
                return True
            else:
                logger.error(f"Erro ao testar CheckStyle: {process.stderr}")
                # Verificar se o erro é apenas sobre formatos
                if "Missing required parameter" in process.stderr or "Usage:" in process.stderr:
                    logger.warning("O erro parece ser apenas sobre o uso do comando, assumindo que o CheckStyle está OK.")
                    return True
                return False
        except Exception as e:
            logger.error(f"Exceção ao testar CheckStyle: {str(e)}")
            return False
    
    def _download_checkstyle(self):
        """Baixa o CheckStyle JAR automaticamente."""
        try:
            import requests
            
            # URL para a versão compatível com Java 8
            url = "https://github.com/checkstyle/checkstyle/releases/download/checkstyle-8.41/checkstyle-8.41-all.jar"
            
            # Caminho para salvar o JAR
            jar_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config"
            )
            os.makedirs(jar_dir, exist_ok=True)
            
            jar_path = os.path.join(jar_dir, "checkstyle.jar")
            
            logger.info(f"Baixando CheckStyle de {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Salvar o arquivo
            total_size = int(response.headers.get('content-length', 0))
            with open(jar_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc="Baixando") as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            logger.info(f"CheckStyle baixado com sucesso para {jar_path}")
            self.checkstyle_jar = jar_path
            
            # Testar se o JAR funciona
            return self._test_checkstyle_jar(jar_path)
            
        except Exception as e:
            logger.error(f"Erro ao baixar CheckStyle: {str(e)}")
            logger.error("Por favor, faça o download manual do CheckStyle JAR e coloque-o na pasta config/")
            return False
    
    def run_checkstyle(self, java_path):
        """
        Executa o CheckStyle em um arquivo ou diretório Java.
        
        Args:
            java_path: Caminho para o arquivo ou diretório Java
            
        Returns:
            str: Saída do CheckStyle em formato XML
        """
        try:
            # Verificar se o caminho existe
            if not os.path.exists(java_path):
                logger.error(f"Caminho não encontrado: {java_path}")
                return None
            
            # Verificar se há arquivos Java no diretório
            if os.path.isdir(java_path):
                has_java_files = False
                for root, _, files in os.walk(java_path):
                    if any(file.endswith(".java") for file in files):
                        has_java_files = True
                        break
                
                if not has_java_files:
                    logger.warning(f"Nenhum arquivo Java encontrado em: {java_path}")
                    return f"<checkstyle version='8.0'></checkstyle>"
            
            # Preparar o comando
            cmd = [
                "java", "-jar", self.checkstyle_jar,
                "-c", self.config_path,
                "-f", "xml",  # Formato de saída XML
                java_path
            ]
            
            logger.info(f"Executando CheckStyle com comando: {' '.join(cmd)}")
            
            # Executar o comando
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            # Verificar resultado
            if process.returncode != 0:
                logger.error(f"CheckStyle falhou com código de saída: {process.returncode}")
                logger.error(f"Erro: {process.stderr}")
                if process.stdout and len(process.stdout) > 0:
                    logger.info(f"Saída: {process.stdout[:200]}...")
                return None
            
            # Verificar se a saída está vazia
            if not process.stdout or process.stdout.strip() == "":
                logger.warning(f"CheckStyle retornou saída vazia para: {java_path}")
                return f"<checkstyle version='8.0'></checkstyle>"
            
            logger.info(f"CheckStyle executado com sucesso em: {java_path}")
            return process.stdout
            
        except Exception as e:
            logger.error(f"Erro ao executar CheckStyle em {java_path}: {str(e)}")
            return None
    
    def parse_checkstyle_output(self, xml_output):
        """
        Analisa a saída XML do CheckStyle.
        
        Args:
            xml_output: Saída XML do CheckStyle
            
        Returns:
            dict: Resultados estruturados da análise
        """
        if not xml_output:
            return {"error": "Saída vazia do CheckStyle"}
        
        try:
            # Se o XML já tiver o formato de saída vazia, retornar estrutura vazia
            if xml_output.strip() == "<checkstyle version='8.0'></checkstyle>":
                return {
                    "code_smells": [],
                    "summary": {
                        "total_issues": 0,
                        "issues_by_severity": {},
                        "issues_by_type": {}
                    }
                }
            
            # Estrutura para armazenar os resultados
            results = {
                "code_smells": [],
                "summary": {
                    "total_issues": 0,
                    "issues_by_severity": {},
                    "issues_by_type": {}
                }
            }
            
            # Parse do XML
            try:
                root = ET.fromstring(xml_output)
            except ET.ParseError as e:
                logger.error(f"Erro ao analisar XML: {str(e)}")
                logger.error(f"XML recebido: {xml_output[:200]}...")
                return {"error": f"Erro ao analisar XML: {str(e)}"}
            
            # Processar cada arquivo
            for file_elem in root.findall(".//file"):
                file_name = file_elem.get("name")
                
                # Processar cada erro (potencial code smell)
                for error in file_elem.findall("./error"):
                    line = error.get("line")
                    column = error.get("column")
                    severity = error.get("severity")
                    message = error.get("message")
                    source = error.get("source")
                    
                    # Extrair o tipo de code smell do source
                    code_smell_type = source.split(".")[-1] if source else "Unknown"
                    
                    # Adicionar à lista de code smells
                    code_smell = {
                        "file": file_name,
                        "line": line,
                        "column": column,
                        "severity": severity,
                        "message": message,
                        "source": source,
                        "type": code_smell_type
                    }
                    
                    results["code_smells"].append(code_smell)
                    
                    # Atualizar sumário
                    results["summary"]["total_issues"] += 1
                    
                    # Contar por severidade
                    if severity not in results["summary"]["issues_by_severity"]:
                        results["summary"]["issues_by_severity"][severity] = 0
                    results["summary"]["issues_by_severity"][severity] += 1
                    
                    # Contar por tipo
                    if code_smell_type not in results["summary"]["issues_by_type"]:
                        results["summary"]["issues_by_type"][code_smell_type] = 0
                    results["summary"]["issues_by_type"][code_smell_type] += 1
            
            return results
            
        except ET.ParseError as e:
            logger.error(f"Erro ao analisar XML do CheckStyle: {str(e)}")
            return {"error": f"Erro ao analisar XML: {str(e)}"}
        except Exception as e:
            logger.error(f"Erro ao processar resultados do CheckStyle: {str(e)}")
            return {"error": f"Erro ao processar resultados: {str(e)}"}
    
    def analyze_repository(self, repo_path):
        """
        Analisa um repositório Java inteiro com o CheckStyle.
        
        Args:
            repo_path: Caminho para o repositório
            
        Returns:
            dict: Resultados da análise
        """
        logger.info(f"Analisando repositório: {repo_path}")
        
        # Verificar se o diretório existe
        if not os.path.exists(repo_path):
            logger.error(f"Repositório não encontrado: {repo_path}")
            return {"error": "Repositório não encontrado"}
        
        # Executar CheckStyle no repositório
        xml_output = self.run_checkstyle(repo_path)
        
        # Se a saída for None, houve um erro na execução
        if xml_output is None:
            logger.error(f"Falha ao executar CheckStyle no repositório: {repo_path}")
            return {"error": "Falha ao executar CheckStyle"}
        
        # Analisar resultados
        results = self.parse_checkstyle_output(xml_output)
        
        # Adicionar informações sobre o repositório
        repo_name = os.path.basename(repo_path)
        results["repository"] = {
            "name": repo_name,
            "path": repo_path
        }
        
        # Salvar resultados
        self._save_results(results, repo_name)
        
        return results
    
    def _save_results(self, results, repo_name):
        """
        Salva os resultados da análise em um arquivo JSON.
        
        Args:
            results: Resultados da análise
            repo_name: Nome do repositório
        """
        # Substituir caracteres inválidos no nome do arquivo
        safe_repo_name = repo_name.replace("/", "_").replace("\\", "_")
        
        # Caminho do arquivo de saída
        output_file = os.path.join(self.output_dir, f"{safe_repo_name}_checkstyle.json")
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Resultados salvos em: {output_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {str(e)}")
    
    def analyze_multiple_repositories(self, repo_paths):
        """
        Analisa múltiplos repositórios.
        
        Args:
            repo_paths: Lista de caminhos para os repositórios
            
        Returns:
            dict: Resultados consolidados
        """
        all_results = {}
        
        for repo_path in tqdm(repo_paths, desc="Analisando repositórios com CheckStyle"):
            repo_name = os.path.basename(repo_path)
            try:
                repo_results = self.analyze_repository(repo_path)
                all_results[repo_name] = repo_results
            except Exception as e:
                logger.error(f"Erro ao analisar repositório {repo_name}: {str(e)}")
                all_results[repo_name] = {"error": str(e)}
        
        return all_results