"""
Configuração dos testes: copia a pasta Data/ para um diretório temporário e
aponta a API para ela (variável PETVERDE_DATA_DIR). Assim, os testes de POST
não alteram os arquivos versionados do repositório.
"""

import os
import pathlib
import shutil
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parents[1]

_pasta_temporaria = pathlib.Path(tempfile.mkdtemp(prefix="petverde_testes_"))
shutil.copytree(RAIZ / "Data", _pasta_temporaria / "Data")
# Remove produtos enviados em execuções anteriores, para os testes partirem do zero.
(_pasta_temporaria / "Data" / "Processed" / "produtos_enviados_api.csv").unlink(missing_ok=True)
os.environ["PETVERDE_DATA_DIR"] = str(_pasta_temporaria / "Data")

sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "Code" / "Deployment"))
sys.path.insert(0, str(RAIZ / "Code" / "Modeling"))
