# dis-ultrassom

Trabalho da disciplina ICSM31 - Desenvolvimento Integrado de Sistemas

Sistema de reconstrução de imagens de ultrassom usando algoritmos iterativos (CGNE e CGNR) com implementações em Python e C++.

## Planejamento
![planejamento](./Planejamento.png)

## Setup

### Dependências C++

Utilize o nix para instalar as dependencias do projeto: https://nixos.org/download/

Ou instale manualmente:
* **Armadillo**: https://arma.sourceforge.net/
* **CMake**: https://cmake.org/download/
* **pkg-config**: Instale via gerenciador de pacotes da sua distro
* **doctest**: https://github.com/doctest/doctest/blob/master/doc/markdown/build-systems.md
* **httplib**: Incluído via git submodule (cpp-httplib)
* **lodepng**: Incluído no projeto

### Dependências Python

O projeto usa:
* **[NixOS (shell.nix)](https://nixos.org/)**
* **[uv](https://github.com/astral-sh/uv)**
* **[Ruff](https://docs.astral.sh/ruff/)**
* **[Pytest](https://docs.pytest.org/)**

No terminal, na raiz do repositório:
```bash
nix-shell
```

Instalar dependências Python:
```bash
make install
```

## Build

Compilar projeto C++:
```bash
make build
```

## Tests

Executar todos os testes (C++ e Python):
```bash
make test
```

Ou separadamente:
```bash
make test-cpp    # Testes C++ com doctest
make test-py     # Testes Python com pytest
```

## Executando os Servidores

### Servidor Python (FastAPI + Multiprocessing)

Iniciar servidor com 4 workers (padrão):
```bash
make run
```

Ou especificar número de workers:
```bash
make run WORKERS=8
```

O servidor inicia na porta **8000**.

### Servidor C++ (httplib + Threads)

Iniciar servidor com 4 workers (padrão):
```bash
make run-cpp
```

Ou especificar número de workers:
```bash
make run-cpp WORKERS=8
```

O servidor inicia na porta **8000**.

## Cliente de Simulação

O cliente envia requisições de reconstrução para o servidor:

```bash
uv run client 8000
```

Gera relatório CSV com métricas de cada job processado.

## Benchmark de Workers

### Python

Para cada configuração de workers (1, 2, 4, 6, 8, 10, 12):

**Terminal 1** - Iniciar servidor:
```bash
make run WORKERS=1
```

**Terminal 2** - Executar simulação:
```bash
uv run client 8000
```

**Terminal 1** - Parar servidor (Ctrl+C) e mover CSV:
```bash
mv reconstruction_report.csv workers_results/python/report_1w.csv
```

Repetir para todos os valores de workers.

### C++

Para cada configuração de workers:

**Terminal 1** - Iniciar servidor:
```bash
make run-cpp WORKERS=1
```

**Terminal 2** - Executar simulação:
```bash
uv run client 8000
```

**Terminal 1** - Parar servidor (Ctrl+C) e mover CSV:
```bash
mv reconstruction_report_cpp.csv workers_results/cpp/report_1w.csv
```

Repetir para todos os valores de workers.

### Análise de Benchmark

Após coletar todos os CSVs:

```bash
make analyze-benchmark-py     # Gera workers_results/python/benchmark_analysis_python.png
make analyze-benchmark-cpp    # Gera workers_results/cpp/benchmark_analysis_cpp.png
```

Os gráficos mostram 3 métricas:
- Tempo médio de execução (ms)
- Uso médio de CPU (%)
- Uso médio de RAM (MB)

## Comparação Python vs C++

Execute 100 jobs em cada servidor e compare:

**Python:**
```bash
make run WORKERS=4
uv run client 8000
# Gera: reconstruction_report.csv
```

**C++:**
```bash
make run-cpp WORKERS=4
uv run client 8000
# Gera: reconstruction_report_cpp.csv
```

**Análise comparativa:**
```bash
uv run python analyze_comparison.py
# Gera: comparison_analysis.png
```

O gráfico mostra comparação temporal de 3 métricas ao longo dos jobs:
- Tempo de execução
- Uso de CPU
- Uso de RAM

## Estrutura de Resultados

```
workers_results/
├── python/
│   ├── report_1w.csv, report_2w.csv, ..., report_12w.csv
│   └── benchmark_analysis_python.png
└── cpp/
    ├── report_1w.csv, report_2w.csv, ..., report_12w.csv
    └── benchmark_analysis_cpp.png

reconstruction_report.csv       # Python (último run)
reconstruction_report_cpp.csv   # C++ (último run)
comparison_analysis.png         # Comparação Python vs C++
```

## Lint e Format

```bash
make format    # Formatar código Python com ruff
make lint      # Verificar código Python com ruff
make check     # format + lint + test
```

## Clean

Remover imagens geradas:
```bash
make clear
```
