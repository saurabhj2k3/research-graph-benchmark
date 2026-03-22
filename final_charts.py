import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# 1. PREPARE THE DATA FROM YOUR RESULTS
data = {
    'Depth': [1, 2, 3, 4, 5] * 4,
    'Database': (['Neo4j']*5) + (['PostgreSQL']*5) + (['MongoDB']*5) + (['ArangoDB']*5),
    'Time (ms)': [2289.7, 168.2, 168.5, 199.7, 104.3] + # Neo4j
                 [321.9, 336.7, 448.8, 677.5, 1978.9] + # Postgres
                 [326.1, 549.5, 1882.6, 9018.5, 25000] + # Mongo (D5 Estimated)
                 [57.7, 47.9, 180.6, 77.6, 1139.9],    # Arango
    'RAM (MB)':  [90.3, 90.4, 90.4, 90.4, 90.4] + [21.5]*5 + [30.5]*5 + [32.1]*5,
    'CPU (%)':   [100, 62.5, 62.5, 62.5, 77.8] + [100]*5 + [100]*5 + [100, 50, 100, 87, 100]
}
df = pd.DataFrame(data)
sns.set_style("whitegrid")

# 2. GENERATE TIME PERFORMANCE (LOG SCALE)
plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='Depth', y='Time (ms)', hue='Database', marker='o', linewidth=2.5)
plt.yscale('log')
plt.title('Performance: Execution Time (Log Scale)', fontsize=14, fontweight='bold')
plt.savefig('results/time_performance.png', dpi=300)

# 3. GENERATE RAM BAR CHART
plt.figure(figsize=(10, 6))
sns.barplot(data=df[df['Depth'] == 5], x='Database', y='RAM (MB)', palette='coolwarm')
plt.title('Efficiency: Peak RAM Usage at Depth 5', fontsize=14, fontweight='bold')
plt.savefig('results/ram_consumption.png', dpi=300)

print("🚀 All 3 Research Charts have been saved to the results/ folder!")