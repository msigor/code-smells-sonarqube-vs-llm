import os
import subprocess
from dotenv import load_dotenv
from pathlib import Path

# Carrega o .env da pasta config/
env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(dotenv_path=env_path)

SONARQUBE_URL = os.getenv("SONARQUBE_URL")
SONARQUBE_TOKEN = os.getenv("SONARQUBE_TOKEN")

# Caminhos base
REPO_PATH = os.path.abspath(os.path.join("..", "data", "repos"))
OUTPUT_DIR = os.path.abspath(os.path.join("..", "data", "sonarqube"))

os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_sonar_scanner(repo_name, repo_dir):
    project_key = repo_name.replace("/", "_")

    sonar_cmd = [
        "sonar-scanner",
        f"-Dsonar.projectKey={project_key}",
        f"-Dsonar.sources=.",
        f"-Dsonar.host.url={SONARQUBE_URL}",
        f"-Dsonar.login={SONARQUBE_TOKEN}",
        f"-Dsonar.projectBaseDir={repo_dir}",
        f"-Dsonar.issuesReport.json.enable=true",  # Nem sempre funciona em versões novas
        f"-Dsonar.issuesReport.path={os.path.join(OUTPUT_DIR, project_key + '.json')}",
    ]

    print(f"🔍 Analisando: {repo_name}")
    result = subprocess.run(sonar_cmd, cwd=repo_dir, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Erro ao analisar {repo_name}:")
        print(result.stderr)
    else:
        print(f"✅ Análise concluída: {repo_name}")

def process_all_repos():
    for repo_name in os.listdir(REPO_PATH):
        repo_dir = os.path.join(REPO_PATH, repo_name)
        if os.path.isdir(repo_dir):
            run_sonar_scanner(repo_name, repo_dir)

if __name__ == "__main__":
    process_all_repos()
