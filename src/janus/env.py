"""Carregador leve de arquivos .env sem dependências externas."""

from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: str | Path = ".env", *, override: bool = False) -> bool:
    """Carrega pares CHAVE=VALOR de um arquivo .env para os.environ.

    Args:
        path: Caminho do arquivo .env.
        override: Se True, sobrescreve variáveis já existentes no ambiente.

    Returns:
        True se o arquivo existia e foi lido; False caso contrário.
    """
    env_path = Path(path)
    if not env_path.is_file():
        return False

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        if line.startswith("export "):
            line = line[len("export ") :].strip()

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]

        if key and (override or key not in os.environ):
            os.environ[key] = value

    return True
