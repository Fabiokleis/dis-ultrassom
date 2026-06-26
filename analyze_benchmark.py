#!/usr/bin/env python3
"""Analise visual de benchmark de workers."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_all_reports(results_dir: Path) -> pd.DataFrame:
    all_data = []
    for report_path in sorted(results_dir.glob("report_*w.csv")):
        num_workers = int(report_path.stem.split("_")[1].replace("w", ""))
        df = pd.read_csv(report_path)
        df["num_workers"] = num_workers
        all_data.append(df)
    
    if not all_data:
        raise ValueError("Nenhum relatorio encontrado")
    
    return pd.concat(all_data, ignore_index=True)


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    completed = df[df["status"] == "completed"]
    
    metrics = completed.groupby("num_workers").agg({
        "job_id": "count",
        "duration_ms": "mean",
        "cpu_percent": "mean",
        "ram_mb": "mean",
    }).reset_index()
    
    metrics.columns = ["num_workers", "total_jobs", "avg_duration_ms", "avg_cpu", "avg_ram"]
    
    return metrics


def plot_analysis(metrics: pd.DataFrame, output_dir: Path, lang: str):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    title = f"Analise de Performance por Workers - {lang.upper()}"
    fig.suptitle(title, fontsize=14)
    
    x_labels = metrics["num_workers"].astype(str)
    x_pos = range(len(metrics))
    
    # Duration
    ax1 = axes[0]
    ax1.bar(x_pos, metrics["avg_duration_ms"], color="#2E86AB", alpha=0.8, edgecolor="black", linewidth=1.2)
    ax1.set_xlabel("Workers")
    ax1.set_ylabel("ms")
    ax1.set_title("Tempo Medio de Execucao")
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(x_labels)
    ax1.grid(axis="y", alpha=0.3)
    for i, v in enumerate(metrics["avg_duration_ms"]):
        ax1.text(i, v, f'{v:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # CPU
    ax2 = axes[1]
    ax2.bar(x_pos, metrics["avg_cpu"], color="#A23B72", alpha=0.8, edgecolor="black", linewidth=1.2)
    ax2.set_xlabel("Workers")
    ax2.set_ylabel("%")
    ax2.set_title("CPU Medio")
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(x_labels)
    ax2.grid(axis="y", alpha=0.3)
    for i, v in enumerate(metrics["avg_cpu"]):
        ax2.text(i, v, f'{v:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # RAM
    ax3 = axes[2]
    ax3.bar(x_pos, metrics["avg_ram"], color="#F18F01", alpha=0.8, edgecolor="black", linewidth=1.2)
    ax3.set_xlabel("Workers")
    ax3.set_ylabel("MB")
    ax3.set_title("RAM Medio")
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(x_labels)
    ax3.grid(axis="y", alpha=0.3)
    for i, v in enumerate(metrics["avg_ram"]):
        ax3.text(i, v, f'{v:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plot_path = output_dir / f"benchmark_analysis_{lang}.png"
    plt.savefig(plot_path, dpi=200, bbox_inches="tight")
    
    return plot_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 analyze_benchmark.py <results_dir> <lang>")
        print("  lang: python ou cpp")
        sys.exit(1)
    
    results_dir = Path(sys.argv[1])
    lang = sys.argv[2].lower()
    
    if lang not in ["python", "cpp"]:
        print("Erro: lang deve ser 'python' ou 'cpp'")
        sys.exit(1)
    
    if not results_dir.exists():
        print(f"Erro: {results_dir} nao encontrado")
        sys.exit(1)
    
    df = load_all_reports(results_dir)
    metrics = calculate_metrics(df)
    
    print(f"\n{lang.upper()} - Benchmark de Workers")
    print(f"Jobs totais: {len(df)}")
    print(f"Configuracoes: {sorted(df['num_workers'].unique())}\n")
    
    print(metrics[["num_workers", "total_jobs", "avg_duration_ms", "avg_cpu", "avg_ram"]].to_string(index=False))
    
    plot_path = plot_analysis(metrics, results_dir, lang)
    print(f"\nGrafico salvo: {plot_path}")


if __name__ == "__main__":
    main()
