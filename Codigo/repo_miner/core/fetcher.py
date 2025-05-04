import os
import subprocess
from repo_miner.config.settings import REPOSITORIES, MAX_REPOS, REPO_CLONE_PATH, GITHUB_TOKEN

def clone_repositories():
    os.makedirs(REPO_CLONE_PATH, exist_ok=True)
    
    for repo in REPOSITORIES[:MAX_REPOS]:
        repo_name = repo.split("/")[-1]
        dest_path = os.path.join(REPO_CLONE_PATH, repo_name)

        if os.path.exists(dest_path):
            print(f"[!] Repositório já existe: {repo_name}")
            continue

        if GITHUB_TOKEN:
            url = f"https://{GITHUB_TOKEN}@github.com/{repo}.git"
        else:
            url = f"https://github.com/{repo}.git"

        print(f"[*] Clonando {url} para {dest_path}...")
        try:
            subprocess.run(["git", "clone", url, dest_path], check=True)
            print(f"[✔] Clonado: {repo_name}")
        except subprocess.CalledProcessError:
            print(f"[x] Falha ao clonar: {repo}")
