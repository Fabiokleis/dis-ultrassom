#!/usr/bin/env python3
"""Analise comparativa: Python vs C++"""

import matplotlib.pyplot as plt
import pandas as pd


def load_data():
    py_df = pd.read_csv("reconstruction_report.csv")
    cpp_df = pd.read_csv("reconstruction_report_cpp.csv")
    
    py_df = py_df[py_df['status'] == 'completed'].copy()
    cpp_df = cpp_df[cpp_df['status'] == 'completed'].copy()
    
    py_df['end_time'] = pd.to_datetime(py_df['end_time'])
    cpp_df['end_time'] = pd.to_datetime(cpp_df['end_time'])
    
    py_df = py_df.sort_values('end_time').reset_index(drop=True)
    cpp_df = cpp_df.sort_values('end_time').reset_index(drop=True)
    
    return py_df, cpp_df


def calculate_metrics(df):
    return {
        'duration_ms': df['duration_ms'].mean(),
        'cpu_percent': df['cpu_percent'].mean(),
        'ram_mb': df['ram_mb'].mean(),
        'total_jobs': len(df),
    }


def plot_temporal_comparison(py_df, cpp_df):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Comparacao Temporal: Python vs C++", fontsize=14)
    
    py_df['job_index'] = range(len(py_df))
    cpp_df['job_index'] = range(len(cpp_df))
    
    ax1 = axes[0]
    ax1.plot(py_df['job_index'], py_df['duration_ms'], 
            label='Python', color='#2E86AB', linewidth=2, alpha=0.7)
    ax1.plot(cpp_df['job_index'], cpp_df['duration_ms'], 
            label='C++', color='#E63946', linewidth=2, alpha=0.7)
    ax1.set_xlabel("Job Index")
    ax1.set_ylabel("ms")
    ax1.set_title("Tempo de Execucao")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2 = axes[1]
    ax2.plot(py_df['job_index'], py_df['cpu_percent'], 
            label='Python', color='#2E86AB', linewidth=2, alpha=0.7)
    ax2.plot(cpp_df['job_index'], cpp_df['cpu_percent'], 
            label='C++', color='#E63946', linewidth=2, alpha=0.7)
    ax2.set_xlabel("Job Index")
    ax2.set_ylabel("%")
    ax2.set_title("Uso de CPU")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    ax3 = axes[2]
    ax3.plot(py_df['job_index'], py_df['ram_mb'], 
            label='Python', color='#2E86AB', linewidth=2, alpha=0.7)
    ax3.plot(cpp_df['job_index'], cpp_df['ram_mb'], 
            label='C++', color='#E63946', linewidth=2, alpha=0.7)
    ax3.set_xlabel("Job Index")
    ax3.set_ylabel("MB")
    ax3.set_title("Uso de RAM")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('comparison_analysis.png', dpi=200, bbox_inches='tight')


def print_summary(py_df, cpp_df, py_metrics, cpp_metrics):
    print(f"\nJobs analisados: Python={py_metrics['total_jobs']}, C++={cpp_metrics['total_jobs']}")
    
    print(f"\n{'Metrica':<25} {'Python':>12} {'C++':>12} {'Diferenca':>12}")
    print("-" * 65)
    
    for metric in ['duration_ms', 'cpu_percent', 'ram_mb']:
        py_val = py_metrics[metric]
        cpp_val = cpp_metrics[metric]
        diff_pct = ((cpp_val - py_val) / py_val) * 100
        
        print(f"{metric:<25} {py_val:>12.2f} {cpp_val:>12.2f} {diff_pct:>11.2f}%")
    
    print("\nGrafico salvo: comparison_analysis.png")


def main():
    py_df, cpp_df = load_data()
    
    py_metrics = calculate_metrics(py_df)
    cpp_metrics = calculate_metrics(cpp_df)
    
    print_summary(py_df, cpp_df, py_metrics, cpp_metrics)
    plot_temporal_comparison(py_df, cpp_df)


if __name__ == "__main__":
    main()
