import os
import random
from enum import Enum
import httpx, time
import json
from pathlib import Path
from server.models import (
    AlgorithmModel,
    ScaleModel,
    SignalModel
)

LINK = "http://localhost:8000"
SIMULATION_FILE = "requests.json"
SIMULATION_SAMPLES = 1
SIMULATION_MAX_WAIT_TIME = 5

FILES = {
    30: {
        1: open('G-1.csv', 'rb'),
        2: open('G-2.csv', 'rb'),
        3: open('G-3.csv', 'rb')
    },
    60: {
        1: open('G-4.csv', 'rb'),
        2: open('G-5.csv', 'rb'),
        3: open('G-6.csv', 'rb')
    }
}

class Request():

    wait_time: int
    algorithm: AlgorithmModel | None
    scale: ScaleModel | None
    signal_id: SignalModel
    gain: bool | None
    
    def __init__(self, wait_time: int, algorithm: AlgorithmModel = None, scale: ScaleModel = None, signal_id: SignalModel = None, gain: bool = None):
        self.algorithm = algorithm if algorithm is not None else AlgorithmModel.random_choice()
        self.scale = scale if scale is not None else ScaleModel.random_choice()
        self.signal_id = signal_id if signal_id is not None else SignalModel.random_choice()
        self.gain = gain if gain is not None else 1 == random.randint(0, 1)
        self.wait_time = wait_time

    def __str__(self):
        return f"Algorithm: {AlgorithmModel(self.algorithm)}, Sinal {SignalModel(self.signal_id)}, Escala: {ScaleModel(self.scale)}, Tempo de Espera: {self.wait_time}"
        
    def to_dict(self):
        """Converte o objeto em um dicionário para poder salvar em JSON."""
        return {
            "algorithm": self.algorithm,
            "scale": self.scale,
            "signal_id": self.signal_id,
            "wait_time": self.wait_time,
            "gain": self.gain
        }

    def post_request(self):
        file = FILES[self.scale][self.signal_id]
        files = { "signal": (os.path.basename(file.name), file, "text/csv") }
        req = self.to_dict()
        params = { "algorithm": self.algorithm, "scale": self.scale, "signal_id": self.signal_id, "gain": self.gain }
        print(params)
        r = httpx.post(LINK+"/ultrassom", params=params, files=files)
        print(r.text)

def create_requests(n, max_wait_time):
    order = []
    for _ in range(n):
        wait_time = random.randint(1, max_wait_time)
        order.append(Request(wait_time))
    return order

def initialize_requests():
    caminho_arquivo = Path(SIMULATION_FILE)
    requests = []

    if caminho_arquivo.is_file():
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            dados_json = json.load(f)
            for d in dados_json:
                requests.append(Request(d["wait_time"], d["algorithm"], d["scale"], d["signal_id"], d["gain"]))

            print(f"Carregados {len(requests)} requests do arquivo.")
    else:
        requests = create_requests(SIMULATION_SAMPLES, SIMULATION_MAX_WAIT_TIME)
        dados_para_salvar = [req.to_dict() for req in requests]
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados_para_salvar, f, indent=4)
        print("Novo arquivo 'requests.json' criado com sucesso.")

    if len(requests) > 0:
        print(f"Exemplo do primeiro request - {requests[0]})")
    return requests


def run_requests():
    requests = initialize_requests()
    for r in requests:
        time.sleep(r.wait_time)
        r.post_request()
        

def main():
    run_requests()
    for (_, files) in FILES.items():
        for (_, file) in files.items():
            file.close()
    
if __name__ == "__main__":
    main()
