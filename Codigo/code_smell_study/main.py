import os
import json
from pathlib import Path
from config.settings import REPO_CLONE_PATH, REPOSITORIES, MAX_REPOS, CODE_EXTENSIONS
from core.llm_analyzer import split_into_chunks, analyze_with_llm


def main():
    output_root = Path("code_smell_study/data/llm")
    output_root.mkdir(parents=True, exist_ok=True)

    for repo_full in REPOSITORIES[:MAX_REPOS]:
        repo_name = repo_full.split("/")[-1]
        repo_path = REPO_CLONE_PATH / repo_full.replace("/", os.sep)
        target_dir = output_root / repo_name
        target_dir.mkdir(parents=True, exist_ok=True)

        for file in repo_path.rglob("*"):
            if file.suffix in CODE_EXTENSIONS:
                code = file.read_text(encoding="utf-8", errors="ignore")
                for idx, chunk in enumerate(split_into_chunks(code), start=1):
                    result = analyze_with_llm(chunk)
                    out = {
                        "repo": repo_name,
                        "file": str(file.relative_to(repo_path)),
                        "chunk_index": idx,
                        "result": result,
                    }
                    fname = file.relative_to(repo_path).as_posix().replace('/', '__')
                    (target_dir / f"{fname}_chunk{idx}.json").write_text(
                        json.dumps(out, ensure_ascii=False, indent=2)
                    )
                    print(f"[LLM] {repo_name}/{file.name} chunk {idx} salvo.")


if __name__ == '__main__':
    main()