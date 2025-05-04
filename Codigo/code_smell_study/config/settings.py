# code_smell_study/config/settings.py
from pathlib import Path
from dotenv import load_dotenv
import os

# carrega variáveis de .env (OPENAI_API_KEY, GITHUB_TOKEN opcional)
load_dotenv(dotenv_path=Path(__file__).parent / '.env')

# paths e repositórios
REPO_CLONE_PATH = Path("repo_miner/data/raw_repos")
MAX_REPOS        = 1
REPOSITORIES     = ["ArjanCodes/2021-code-smells"]

# extensões de arquivo a processar
CODE_EXTENSIONS = {
    '.py', '.java', '.js', '.ts', '.go', '.cpp', '.c',
    '.cs', '.kt', '.swift', '.rb', '.php'
}

# limite de tokens por chunk
MAX_TOKENS = 120_000

# modelo e prompt
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

# prompt enxuto: será passado como mensagem de sistema
SYSTEM_PROMPT = """Você é um detector automatizado de code smells.
Para cada trecho de código que receber, retorne somente um objeto JSON com:
- smells_detectados: lista de nomes de smells
- descricao: mapeamento smell→descrição muito breve
- localizacao: smell→"linha_inicial-linha_final"
- confianca: smell→alto/médio/baixo

Regras:
- Retorne apenas o JSON, sem texto extra.
- Use descrições de no máximo uma linha.
- Seja conciso para economizar tokens."""

# aqui o template só injeta o código
PROMPT_TEMPLATE = "{code}"
