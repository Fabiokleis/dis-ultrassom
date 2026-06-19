import random
import json
from pathlib import Path

# Nota: Em Python, boas práticas sugerem iniciar classes com letra maiúscula (Request)
class Request:
    def __init__(self, wait_time, scale=None, signal_id=None):
        # Permitir passar scale e signal_id ao recriar o objeto a partir do JSON
        self.scale = scale if scale is not None else random.randint(1, 2)
        self.signal_id = signal_id if signal_id is not None else random.randint(1, 3)
        self.wait_time = wait_time

    def to_dict(self):
        """Converte o objeto em um dicionário para poder salvar em JSON."""
        return {
            "scale": self.scale,
            "signal_id": self.signal_id,
            "wait_time": self.wait_time
        }

def create_requests(n, max_wait_time):
    order = []
    for _ in range(n):
        wait_time = random.randint(1, max_wait_time)
        order.append(Request(wait_time))
    return order

def start():
    caminho_arquivo = Path("requests.json")

    if caminho_arquivo.is_file():
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados_json = json.load(f)
        
        # Reconverte os dicionários do JSON de volta para objetos Request
        requests = [
            Request(d["wait_time"], d["scale"], d["signal_id"]) 
            for d in dados_json
        ]
        print(f"Carregados {len(requests)} requests do arquivo.")
    else:
        # Cria a lista de objetos
        requests = create_requests(100, 5)
        
        # Converte a lista de objetos em uma lista de dicionários para o JSON aceitar
        dados_para_salvar = [req.to_dict() for req in requests]
        
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados_para_salvar, f, indent=4) # indent=4 deixa o arquivo legível
        print("Novo arquivo 'requests.json' criado com sucesso.")

    # Apenas para testar se os objetos funcionam:
    if requests:
        print(f"Exemplo do primeiro request - ID do Sinal: {requests[0].signal_id}, Escala: {requests[0].scale}, Tempo de Espera: {requests[0].wait_time}")

def main():
    start()

if __name__ == "__main__":
    main()