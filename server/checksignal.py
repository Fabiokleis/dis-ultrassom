import numpy as np
from pathlib import Path

# __file__ é o caminho deste script (server/check_shapes.py)
# .parent é a pasta 'server/'
# .parent.parent volta mais uma pasta, chegando na RAIZ do diretório
raiz_projeto = Path(__file__).resolve().parent.parent

for i in range(1, 7):
    file_name = f"G-{i}.csv"
    # Monta o caminho apontando para a raiz do projeto
    path = raiz_projeto / file_name
    
    if path.exists():
        with open(path, "rb") as f:
            file_content = f.read()
        text_data = file_content.decode("utf-8").replace("\n", ",")
        g = np.fromstring(text_data, sep=",")
        
        print(f"Arquivo {file_name} -> g.shape[0] = {g.shape[0]}")
    else:
        print(f"Arquivo {file_name} -> Não encontrado em: {path}")