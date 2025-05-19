
"""
Script principal para o minerador de repositórios.
Este script executa todo o processo de mineração, clonagem e análise de repositórios.
"""

import os
import sys
import argparse
import logging
from dotenv import load_dotenv

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar componentes do projeto
from core.fetcher import GitHubRepoMiner
from config.settings import (
    REPO_CLONE_PATH,
    MAX_REPOS,
    MIN_STARS,
    GITHUB_TOKEN
)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("repo_miner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def parse_arguments():
    """Parse os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description='Minerador de repositórios Java populares para análise de code smells.'
    )
    
    parser.add_argument('--token', type=str, help='Token de acesso do GitHub')
    parser.add_argument(
        '--max-repos', 
        type=int, 
        default=MAX_REPOS, 
        help=f'Número máximo de repositórios a clonar (padrão: {MAX_REPOS})'
    )
    parser.add_argument(
        '--min-stars', 
        type=int, 
        default=MIN_STARS, 
        help=f'Número mínimo de estrelas para considerar (padrão: {MIN_STARS})'
    )
    parser.add_argument(
        '--clone-path', 
        type=str, 
        default=REPO_CLONE_PATH, 
        help=f'Diretório onde os repositórios serão clonados (padrão: {REPO_CLONE_PATH})'
    )
    
    return parser.parse_args()

def main():
    """Função principal do script."""
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Obter argumentos da linha de comando
    args = parse_arguments()
    
    # Configurar parâmetros
    token = args.token or GITHUB_TOKEN or os.getenv("GITHUB_TOKEN")
    max_repos = args.max_repos
    min_stars = args.min_stars
    clone_path = args.clone_path
    
    logger.info("Iniciando mineração de repositórios...")
    logger.info(f"Configurações: max_repos={max_repos}, min_stars={min_stars}, clone_path={clone_path}")
    
    # Criar minerador de repositórios
    miner = GitHubRepoMiner(
        token=token,
        max_repos=max_repos,
        min_stars=min_stars,
        clone_path=clone_path
    )
    
    # Minerar repositórios
    repositories = miner.mine_repositories()
    
    if repositories:
        logger.info(f"Mineração concluída! {len(repositories)} repositórios foram clonados.")
        
        # Exibir informações sobre os repositórios
        logger.info("Repositórios clonados:")
        for i, repo in enumerate(repositories, 1):
            logger.info(f"{i}. {repo['full_name']} - {repo['stars']} estrelas - {repo['local_path']}")
    else:
        logger.warning("Nenhum repositório foi clonado. Verifique os logs para mais detalhes.")
    
    logger.info("Processo de mineração finalizado.")

if __name__ == "__main__":
    main()