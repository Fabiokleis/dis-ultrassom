import asyncio
import json
import os
import random
import time
from pathlib import Path

import httpx

from server.models import AlgorithmModel, ScaleModel, SignalModel

SIMULATION_LINK = "http://localhost:8000"
SIMULATION_FILE = "requests.json"
SIMULATION_SAMPLES = 100
SIMULATION_MAX_WAIT_TIME = 5
SIMULATION_NUM_PARALLEL_CLIENTS = 4

SIMULATION_FILES = {
    30: {1: "G-1.csv", 2: "G-2.csv", 3: "G-3.csv"},
    60: {1: "G-4.csv", 2: "G-5.csv", 3: "G-6.csv"},
}


class Request:
    def __init__(
        self,
        wait_time: int,
        algorithm: AlgorithmModel = None,
        scale: ScaleModel = None,
        signal_id: SignalModel = None,
        gain: bool = None,
    ):
        self.algorithm = (
            algorithm
            if algorithm is not None
            else AlgorithmModel.random_choice()
        )
        self.scale = scale if scale is not None else ScaleModel.random_choice()
        self.signal_id = (
            signal_id if signal_id is not None else SignalModel.random_choice()
        )
        self.gain = gain if gain is not None else bool(random.randint(0, 1))
        self.wait_time = wait_time

    def to_dict(self):
        return {
            "algorithm": self.algorithm.value,
            "scale": self.scale.value,
            "signal_id": self.signal_id.value,
            "wait_time": self.wait_time,
            "gain": self.gain,
        }

    async def send(self, client: httpx.AsyncClient, files_content, req_id: int):
        # Espera o tempo aleatório antes de enviar a requisição
        await asyncio.sleep(self.wait_time)
        
        file_data = files_content[(self.scale.value, self.signal_id.value)]

        params = {
            "algorithm": self.algorithm.value,
            "scale": self.scale.value,
            "signal_id": self.signal_id.value,
            "gain": self.gain,
        }

        try:
            start = time.time()
            r = await client.post(
                SIMULATION_LINK + "/ultrassom", params=params, files=file_data
            )
            elapsed = time.time() - start

            return {"id": req_id, "status": r.status_code, "time": elapsed}
        except Exception as e:
            return {"id": req_id, "status": "error", "error": str(e)}


def load_files():
    files_content = {}
    for scale, signals in SIMULATION_FILES.items():
        for signal_id, filepath in signals.items():
            with open(filepath, "rb") as f:
                content = f.read()
                filename = os.path.basename(filepath)
                files_content[(scale, signal_id)] = {
                    "signal": (filename, content, "text/csv")
                }
    return files_content


def load_or_create_requests():
    path = Path(SIMULATION_FILE)

    if path.is_file():
        with open(path) as f:
            data = json.load(f)
            return [
                Request(
                    d["wait_time"],
                    AlgorithmModel(d["algorithm"]),
                    ScaleModel(d["scale"]),
                    SignalModel(d["signal_id"]),
                    d["gain"],
                )
                for d in data
            ]
    else:
        requests = [
            Request(random.randint(1, SIMULATION_MAX_WAIT_TIME))
            for _ in range(SIMULATION_SAMPLES)
        ]
        with open(path, "w") as f:
            json.dump([req.to_dict() for req in requests], f, indent=2)
        return requests


async def run_client_partition(
    client_id: int, requests: list[Request], files_content: dict, start_id: int
):
    """Cada cliente processa suas requisições SEQUENCIALMENTE"""
    async with httpx.AsyncClient(timeout=120.0) as client:
        results = []
        for i, req in enumerate(requests):
            result = await req.send(client, files_content, start_id + i)
            results.append(result)
        return results


async def run_parallel_simulation(num_clients: int):
    print(f"Loading {len(SIMULATION_FILES)} signal files...")
    files_content = load_files()

    print(f"Loading requests from {SIMULATION_FILE}...")
    requests = load_or_create_requests()

    partition_size = len(requests) // num_clients
    partitions = []

    for i in range(num_clients):
        start = i * partition_size
        end = start + partition_size if i < num_clients - 1 else len(requests)
        partitions.append(requests[start:end])

    print(
        f"Starting simulation: {len(requests)} requests, {num_clients} clients"
    )

    start_time = time.time()

    tasks = [
        run_client_partition(
            i,
            partitions[i],
            files_content,
            sum(len(partitions[j]) for j in range(i)),
        )
        for i in range(num_clients)
    ]
    all_results = await asyncio.gather(*tasks)

    total_time = time.time() - start_time
    flat_results = [r for partition in all_results for r in partition]

    successful = sum(
        1
        for r in flat_results
        if isinstance(r.get("status"), int) and r["status"] == 200
    )

    print(f"\nResults: {successful}/{len(flat_results)} successful")
    print(f"Total time: {total_time:.2f}s")
    print(f"Throughput: {successful / total_time:.2f} req/s")


def main():
    asyncio.run(run_parallel_simulation(SIMULATION_NUM_PARALLEL_CLIENTS))


if __name__ == "__main__":
    main()
