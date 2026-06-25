#!/usr/bin/env python3
"""Análise visual de benchmark de workers."""

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
        raise ValueError("Nenhum relatório encontrado")
    
    return pd.concat(all_data, ignore_index=True)


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    completed = df[df["status"] == "completed"]
    
    metrics = completed.groupby("num_workers").agg({
        "job_id": "count",
        "duration_ms": "max",
        "cpu_percent": "mean",
        "ram_mb": "mean",
    }).reset_index()
    
    metrics.columns = ["num_workers", "total_jobs", "max_duration_ms", "avg_cpu", "avg_ram"]
    
    metrics["total_time_s"] = metrics["max_duration_ms"] / 1000
    metrics["throughput"] = metrics["total_jobs"] / metrics["total_time_s"]
    metrics["efficiency"] = metrics["throughput"] / ((metrics["avg_cpu"] + 1) * (metrics["avg_ram"] / 1024))
    
    return metrics


def plot_analysis(metrics: pd.DataFrame, output_dir: Path):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Analise de Performance por Workers", fontsize=14)
    
    x_labels = metrics["num_workers"].astype(str)
    x_pos = range(len(metrics))
    
    # Throughput
    ax1 = axes[0]
    ax1.bar(x_pos, metrics["throughput"], color="#2E86AB", alpha=0.8, edgecolor="black", linewidth=1.2)
    ax1.set_xlabel("Workers")
    ax1.set_ylabel("Throughput (jobs/s)")
    ax1.set_title("Throughput")
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(x_labels)
    ax1.grid(axis="y", alpha=0.3)
    for i, v in enumerate(metrics["throughput"]):
        ax1.text(i, v, f'{v:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # CPU
    ax2 = axes[1]
    ax2.bar(x_pos, metrics["avg_cpu"], color="#A23B72", alpha=0.8, edgecolor="black", linewidth=1.2)
    ax2.set_xlabel("Workers")
    ax2.set_ylabel("CPU (%)")
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
    ax3.set_ylabel("RAM (MB)")
    ax3.set_title("RAM Medio")
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(x_labels)
    ax3.grid(axis="y", alpha=0.3)
    for i, v in enumerate(metrics["avg_ram"]):
        ax3.text(i, v, f'{v:.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plot_path = output_dir / "benchmark_analysis.png"
    plt.savefig(plot_path, dpi=200, bbox_inches="tight")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_benchmark.py <results_dir>")
        sys.exit(1)
    
    results_dir = Path(sys.argv[1])
    if not results_dir.exists():
        print(f"Erro: {results_dir} nao encontrado")
        sys.exit(1)
    
    df = load_all_reports(results_dir)
    metrics = calculate_metrics(df)
    
    print(f"\nJobs totais: {len(df)}")
    print(f"Configuracoes: {sorted(df['num_workers'].unique())}\n")
    
    print(metrics[["num_workers", "total_jobs", "throughput", "total_time_s", "avg_cpu", "avg_ram"]].to_string(index=False))
    
    plot_analysis(metrics, results_dir)
    print(f"\nGrafico: {results_dir}/benchmark_analysis.png")


if __name__ == "__main__":
    main()
