"""
Script para executar a análise de code smells com CheckStyle nos repositórios clonados.
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("run_checkstyle.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description='Executa análise de code smells com CheckStyle em repositórios Java.'
    )
    
    parser.add_argument(
        '--repo-dir', 
        type=str, 
        default='../repo_miner/data/raw_repos',
        help='Diretório contendo os repositórios clonados'
    )
    parser.add_argument(
        '--config', 
        type=str, 
        default='config/checkstyle-config.xml',
        help='Caminho para o arquivo de configuração do CheckStyle'
    )
    parser.add_argument(
        '--jar', 
        type=str, 
        default='config/checkstyle.jar',
        help='Caminho para o arquivo JAR do CheckStyle'
    )
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='../data/checkstyle',
        help='Diretório onde serão salvos os resultados'
    )
    parser.add_argument(
        '--repo-name', 
        type=str, 
        help='Nome específico de um repositório para analisar (opcional)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostrar informações detalhadas durante a execução'
    )
    
    return parser.parse_args()

def main():
    """Função principal."""
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Obter argumentos da linha de comando
    args = parse_arguments()
    
    # Definir nível de log baseado no argumento verbose
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info("Iniciando análise com CheckStyle...")
    
    # Adicionar o diretório atual ao Python path para encontrar os módulos
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    
    # Importar o módulo apenas depois de ajustar o path
    from core.checkstyle_analyzer import CheckStyleAnalyzer
    
    # Converter caminhos relativos para absolutos
    repo_dir = os.path.abspath(args.repo_dir)
    config_path = os.path.abspath(args.config)
    jar_path = os.path.abspath(args.jar)
    output_dir = os.path.abspath(args.output_dir)
    
    logger.info(f"Diretório dos repositórios: {repo_dir}")
    logger.info(f"Arquivo de configuração: {config_path}")
    logger.info(f"Arquivo JAR do CheckStyle: {jar_path}")
    logger.info(f"Diretório de saída: {output_dir}")
    
    # Criar diretório de saída se não existir
    os.makedirs(output_dir, exist_ok=True)
    
    # Verificar se o diretório de repositórios existe
    if not os.path.exists(repo_dir):
        logger.error(f"Diretório de repositórios não encontrado: {repo_dir}")
        return
    
    # Verificar se a configuração existe, se não, criar minimal
    if not os.path.exists(config_path):
        logger.warning(f"Arquivo de configuração não encontrado: {config_path}")
        logger.info("Criando arquivo de configuração mínimo...")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            f.write('''<?xml version="1.0"?>
<!DOCTYPE module PUBLIC "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN" "https://checkstyle.org/dtds/configuration_1_3.dtd">
<module name="Checker">
    <property name="severity" value="warning"/>
    <property name="fileExtensions" value="java"/>
    <module name="TreeWalker">
        <module name="MethodLength">
            <property name="tokens" value="METHOD_DEF"/>
            <property name="max" value="60"/>
        </module>
    </module>
</module>
''')
        logger.info(f"Arquivo de configuração criado em: {config_path}")
    
    # Inicializar analisador
    try:
        analyzer = CheckStyleAnalyzer(
            config_path=config_path,
            output_dir=output_dir,
            checkstyle_jar=jar_path if os.path.exists(jar_path) else None
        )
    except Exception as e:
        logger.error(f"Erro ao inicializar o analisador: {str(e)}")
        return
    
    # Se um repositório específico foi solicitado
    if args.repo_name:
        repo_path = os.path.join(repo_dir, args.repo_name)
        if os.path.exists(repo_path):
            logger.info(f"Analisando repositório específico: {args.repo_name}")
            try:
                analyzer.analyze_repository(repo_path)
            except Exception as e:
                logger.error(f"Erro ao analisar repositório {args.repo_name}: {str(e)}")
        else:
            logger.error(f"Repositório não encontrado: {args.repo_name}")
    else:
        # Analisar todos os repositórios no diretório
        repo_paths = []
        for item in os.listdir(repo_dir):
            item_path = os.path.join(repo_dir, item)
            if os.path.isdir(item_path):
                repo_paths.append(item_path)
        
        if repo_paths:
            logger.info(f"Analisando {len(repo_paths)} repositórios...")
            try:
                analyzer.analyze_multiple_repositories(repo_paths)
            except Exception as e:
                logger.error(f"Erro durante a análise múltipla: {str(e)}")
        else:
            logger.warning(f"Nenhum repositório encontrado em: {repo_dir}")
    
    logger.info("Análise com CheckStyle concluída!")

if __name__ == "__main__":
    main()