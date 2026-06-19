import random
from enum import Enum
import httpx, time
import json
from pathlib import Path

LINK = "http://localhost:8000"
G1 = open('../test_files/G-1.csv', 'rb')
G2 = open('../test_files/G-2.csv', 'rb')
G3 = open('../test_files/G-2.csv', 'rb')
G4 = open('../test_files/G-2.csv', 'rb')
G5 = open('../test_files/G-2.csv', 'rb')
G6 = open('../test_files/G-2.csv', 'rb')

class Algorithm(str, Enum):
    """Algoritmos de reconstrução disponíveis"""
    CGNE = "cgne"
    CGNR = "cgnr"


# Nota: Em Python, boas práticas sugerem iniciar classes com letra maiúscula (Request)
class Request():
    def __init__(self, algorithm: Algorithm, wait_time: int, scale: int = None, signal_id: int = None):
        # Permitir passar scale e signal_id ao recriar o objeto a partir do JSON
        self.algorithm = algorithm
        self.scale = scale if scale is not None else random.choice([30, 60])
        self.signal_id = signal_id if signal_id is not None else random.randint(1, 3)
        self.wait_time = wait_time

    def to_dict(self):
        """Converte o objeto em um dicionário para poder salvar em JSON."""
        return {
            "algorithm": self.algorithm,
            "scale": self.scale,
            "signal_id": self.signal_id,
            "wait_time": self.wait_time
        }
    
    def match_file(self):
        return {
            30: {
                1: G1,
                2: G2,
                3: G3
            },
            60: {
                1: G4,
                2: G5,
                3: G6
            }
        }

        

    def post_request(self):

        headers = {'Content-type': 'multipart/form-data'}

        r = httpx.post(LINK+"/ultrassom", params= self.to_dict(), files = {"file": self.match_file()[self.scale, self.signal_id]}, headers = headers)

        print(r.text)

def create_requests(n, max_wait_time):
    order = []
    for _ in range(n):
        wait_time = random.randint(1, max_wait_time)
        algorithm = random.choice([Algorithm.CGNE, Algorithm.CGNR])
        order.append(Request(algorithm, wait_time))
    return order

def initialize_requests():
    caminho_arquivo = Path("requests.json")

    if caminho_arquivo.is_file():
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados_json = json.load(f)
        
        # Reconverte os dicionários do JSON de volta para objetos Request
        requests = [
            Request(d["algorithm"],d["wait_time"], d["scale"], d["signal_id"]) 
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
    return requests


def run_requests():
    requests = initialize_requests()
    for r in requests:
        time.sleep(r.wait_time)
        r.post_request()
        


def main():
    run_requests()


if __name__ == "__main__":
    main()