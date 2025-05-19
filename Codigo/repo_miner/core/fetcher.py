"""
Módulo para minerar repositórios Java populares do GitHub para análise de code smells.
"""

import os
import json
import logging
import argparse
import subprocess
from datetime import datetime
from github import Github, RateLimitExceededException
from tqdm import tqdm
from dotenv import load_dotenv

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

class GitHubRepoMiner:
    """Classe para minerar repositórios Java populares do GitHub."""
    
    def __init__(self, token=None, max_repos=10, min_stars=1000, clone_path=None):
        """
        Inicializa o minerador de repositórios.
        
        Args:
            token: Token de autenticação para GitHub
            max_repos: Número máximo de repositórios a clonar
            min_stars: Número mínimo de estrelas para considerar
            clone_path: Diretório onde os repositórios serão clonados
        """
        # Carregar variáveis de ambiente
        load_dotenv()
        
        self.github_token = token or os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            logger.warning("Token do GitHub não fornecido. Usando acesso público (limitado).")
        
        self.max_repos = max_repos
        self.min_stars = min_stars
        self.clone_path = clone_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "raw_repos"
        )
        
        # Garantir que o diretório de clone existe
        os.makedirs(self.clone_path, exist_ok=True)
        
        # Inicializar cliente GitHub
        self.github = Github(self.github_token)
    
    def find_popular_repositories(self):
        """
        Encontra repositórios Java populares no GitHub.
        
        Returns:
            list: Lista de repositórios populares
        """
        query = f"language:java stars:>={self.min_stars} fork:false"
        repositories = []
        
        try:
            logger.info(f"Buscando até {self.max_repos} repositórios Java com pelo menos {self.min_stars} estrelas...")
            search_results = self.github.search_repositories(query=query, sort="stars", order="desc")
            
            # Verifica se há resultados
            if search_results.totalCount == 0:
                logger.warning("Nenhum repositório encontrado com os critérios especificados")
                return []
            
            logger.info(f"Total de {search_results.totalCount} repositórios encontrados. Selecionando os {self.max_repos} mais populares.")
            
            # Seleciona apenas o número especificado de repositórios
            for i, repo in enumerate(search_results):
                if i >= self.max_repos:
                    break
                
                repo_info = {
                    "name": repo.name,
                    "full_name": repo.full_name,
                    "html_url": repo.html_url,
                    "clone_url": repo.clone_url,
                    "ssh_url": repo.ssh_url,
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "size_kb": repo.size,
                    "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
                    "language": repo.language,
                    "description": repo.description
                }
                repositories.append(repo_info)
            
        except RateLimitExceededException:
            logger.error("Limite de taxa do GitHub excedido. Tente novamente mais tarde ou use um token.")
        except Exception as e:
            logger.error(f"Erro ao buscar repositórios: {str(e)}")
        
        return repositories
    
    def clone_repository(self, repo_info):
        """
        Clona um repositório do GitHub.
        
        Args:
            repo_info: Dicionário com informações do repositório
            
        Returns:
            str: Caminho para o repositório clonado ou None se falhar
        """
        repo_name = repo_info["full_name"]
        clone_url = repo_info["clone_url"]
        
        # Criar diretório para o repositório
        repo_dir = os.path.join(self.clone_path, repo_name.replace("/", "_"))
        
        # Verificar se o repositório já foi clonado
        if os.path.exists(repo_dir):
            logger.info(f"Repositório {repo_name} já existe localmente em {repo_dir}")
            return repo_dir
        
        # Clonar o repositório
        try:
            logger.info(f"Clonando repositório {repo_name} para {repo_dir}...")
            
            # Construir comando de clone
            cmd = ["git", "clone", clone_url, repo_dir]
            if self.github_token:
                # Adicionar token ao URL para autenticação
                auth_url = clone_url.replace("https://", f"https://{self.github_token}@")
                cmd = ["git", "clone", auth_url, repo_dir]
            
            # Executar comando
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode != 0:
                logger.error(f"Falha ao clonar {repo_name}: {process.stderr}")
                return None
            
            logger.info(f"Repositório {repo_name} clonado com sucesso para {repo_dir}")
            return repo_dir
            
        except Exception as e:
            logger.error(f"Erro ao clonar repositório {repo_name}: {str(e)}")
            return None
    
    def mine_repositories(self):
        """
        Encontra e clona repositórios populares.
        
        Returns:
            list: Lista com informações dos repositórios clonados
        """
        # Encontrar repositórios populares
        repositories = self.find_popular_repositories()
        
        if not repositories:
            logger.warning("Nenhum repositório encontrado para clonar")
            return []
        
        # Clonar repositórios
        cloned_repos = []
        
        for repo in tqdm(repositories, desc="Clonando repositórios"):
            repo_path = self.clone_repository(repo)
            
            if repo_path:
                # Adicionar caminho local aos dados do repositório
                repo["local_path"] = repo_path
                cloned_repos.append(repo)
        
        # Salvar informações dos repositórios
        self._save_repositories_info(cloned_repos)
        
        logger.info(f"Total de {len(cloned_repos)} repositórios clonados com sucesso")
        return cloned_repos
    
    def _save_repositories_info(self, repositories):
        """
        Salva informações dos repositórios em um arquivo JSON.
        
        Args:
            repositories: Lista de dicionários com informações dos repositórios
        """
        if not repositories:
            logger.warning("Nenhuma informação de repositório para salvar")
            return
        
        # Diretório para armazenar informações
        info_dir = os.path.dirname(self.clone_path)
        os.makedirs(info_dir, exist_ok=True)
        
        # Arquivo de saída
        output_file = os.path.join(info_dir, "repositories_info.json")
        
        # Adicionar metadata
        data = {
            "metadata": {
                "count": len(repositories),
                "date_collected": datetime.now().isoformat(),
                "min_stars": self.min_stars,
                "max_stars": max(repo["stars"] for repo in repositories) if repositories else 0
            },
            "repositories": repositories
        }
        
        # Salvar arquivo
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Informações dos repositórios salvas em {output_file}")
        except Exception as e:
            logger.error(f"Erro ao salvar informações dos repositórios: {str(e)}")

def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Minerador de repositórios Java populares do GitHub.')
    parser.add_argument('--token', type=str, help='Token de acesso do GitHub')
    parser.add_argument('--max-repos', type=int, default=10, help='Número máximo de repositórios a clonar')
    parser.add_argument('--min-stars', type=int, default=1000, help='Número mínimo de estrelas para considerar')
    parser.add_argument('--clone-path', type=str, help='Diretório onde os repositórios serão clonados')
    
    args = parser.parse_args()
    
    # Criar minerador
    miner = GitHubRepoMiner(
        token=args.token,
        max_repos=args.max_repos,
        min_stars=args.min_stars,
        clone_path=args.clone_path
    )
    
    # Minerar repositórios
    miner.mine_repositories()

if __name__ == "__main__":
    main()