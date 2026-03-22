import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# --- ACTUAL RESEARCH DATA ---
data = {
    'Depth': [1, 2, 3, 4, 5],
    'PostgreSQL': [320, 3592, 6397, 10744, 13300],
    'MongoDB': [31, 43, 204, 7145, 20000], # 20k used to represent Depth 5 Timeout
    'Neo4j': [2547, 271, 214, 175, 301],
    'ArangoDB': [338, 9, 68, 122, 1081]
}

df = pd.DataFrame(data)
df_melted = df.melt('Depth', var_name='Database Architecture', value_name='Latency (ms)')

plt.figure(figsize=(12, 7))
sns.set_style("whitegrid")
# Using log scale because the difference between 9ms and 20,000ms is too huge for a normal graph
plot = sns.lineplot(data=df_melted, x='Depth', y='Latency (ms)', hue='Database Architecture', marker='o', linewidth=3)

plt.yscale('log') # This is critical for your Viva!
plt.title('Benchmark: 1 Million Records - Graph Traversal Efficiency', fontsize=16, fontweight='bold')
plt.ylabel('Latency in Milliseconds (Log Scale)', fontsize=12)
plt.xlabel('Traversal Depth (Hops)', fontsize=12)
plt.legend(title='Architecture Type')

plt.savefig('results/final_research_plot.png', dpi=300)
print("✅ Final Research Chart saved to results/final_research_plot.png!")
plt.show()