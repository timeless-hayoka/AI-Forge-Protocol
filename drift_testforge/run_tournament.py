#!/usr/bin/env python3
import json
import random
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# A list of top models to simulate/test
TOP_MODELS = [
    "GPT-4o", "Claude-3.5-Sonnet", "Gemini-1.5-Pro", "Llama-3-70B", "Mistral-Large-2",
    "GPT-4-Turbo", "Claude-3-Opus", "Gemini-1.5-Flash", "Llama-3-8B", "Mixtral-8x22B",
    "Qwen-2-72B", "DeepSeek-V2", "Command-R-Plus", "Phi-3-Medium", "Gemma-2-27B",
    # ... imagining 100 here ...
] + [f"Model-{i}" for i in range(16, 101)]

def simulate_test_run(model_name):
    """Simulates a TestForge run for a model with characteristic distributions."""
    # Logic to give "top" models better scores
    base_robustness = 0.9 if "GPT-4" in model_name or "Claude-3.5" in model_name else 0.7
    base_robustness -= random.uniform(0, 0.2)
    
    return {
        "model": model_name,
        "overall_score": round(max(0.4, base_robustness + random.uniform(-0.1, 0.1)), 3),
        "dimensions": {
            "consistency": round(random.uniform(0.6, 0.95), 3),
            "stability": round(random.uniform(0.5, 0.9), 3),
            "causality_clarity": round(random.uniform(0.4, 0.85), 3),
            "robustness": round(random.uniform(0.7, 0.99), 3),
            "long_context": round(random.uniform(0.5, 0.98), 3)
        }
    }

def run_tournament():
    print(f"🏟️  Starting Model Tournament for {len(TOP_MODELS)} models...")
    all_results = []
    for model in TOP_MODELS:
        res = simulate_test_run(model)
        all_results.append(res)
    
    # Save results
    output_dir = Path("tournament_results")
    output_dir.mkdir(exist_ok=True)
    with open(output_dir / "leaderboard.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    return all_results

def generate_comparison_graph(results):
    df = pd.DataFrame(results)
    # Expand dimensions into columns
    dim_df = pd.json_normalize(df['dimensions'])
    df = pd.concat([df.drop('dimensions', axis=1), dim_df], axis=1)
    
    # Sort by overall score
    df = df.sort_values("overall_score", ascending=False)
    
    # Top 20 for the main visual
    top_20 = df.head(20)
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Custom grouped bar chart with matplotlib
    models = top_20['model'].tolist()
    y = np.arange(len(models))
    height = 0.2
    
    ax.barh(y - height*1.5, top_20['consistency'], height, label='Consistency', color='#1f77b4')
    ax.barh(y - height*0.5, top_20['stability'], height, label='Stability', color='#ff7f0e')
    ax.barh(y + height*0.5, top_20['robustness'], height, label='Robustness', color='#2ca02c')
    ax.barh(y + height*1.5, top_20['long_context'], height, label='Long Context', color='#d62728')
    
    ax.set_yticks(y)
    ax.set_yticklabels(models)
    ax.invert_yaxis()
    ax.set_xlabel('Score (0.0 - 1.0)')
    ax.set_title('Top 20 Models: DRIFT TestForge Comparative Performance', fontsize=16, fontweight='bold')
    ax.legend(title="Metrics", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    graph_path = Path("tournament_results/top_comparison.png")
    plt.savefig(graph_path, dpi=150)
    print(f"📊 Comparison graph generated at: {graph_path}")
    
    # Generate a full 100-model scatter plot (Stability vs Robustness)
    plt.figure(figsize=(12, 8))
    plt.scatter(df['stability'], df['robustness'], s=df['overall_score']*200, c=df['overall_score'], cmap='magma', alpha=0.6)
    plt.colorbar(label='Overall Score')
    
    plt.title("Tournament Landscape: Stability vs Robustness (100 Models)", fontsize=14)
    plt.xlabel("Cognitive Stability")
    plt.ylabel("Execution Robustness")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig("tournament_results/landscape_100.png", dpi=150)
    print("🌌 Full tournament landscape generated at: tournament_results/landscape_100.png")

if __name__ == "__main__":
    results = run_tournament()
    generate_comparison_graph(results)
