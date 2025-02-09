import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('Data/quantity_data.csv')

# Convert start column to datetime
df['start'] = pd.to_datetime(df['start'])

# Extract hour and minute from datetime
df['time'] = df['start'].dt.strftime('%H:%M')

# Group by time and calculate statistics
grouped = df.groupby('time')['quantity_value-6060']

mean = grouped.mean()
std = grouped.std()  # Standard deviation

# Create the plot
plt.figure(figsize=(12, 6))
plt.plot(mean.index, mean.values, 'b-', label='Mean Energy Usage')
plt.fill_between(mean.index, 
                 mean.values - std, 
                 mean.values + std, 
                 color='b', alpha=0.1, label='±1 Standard Deviation')
 

# Customize the plot
plt.title('Mean Daily Energy Usage with ±1 Standard Deviation')
plt.xlabel('Time of Day')
plt.ylabel('Energy Value')
plt.grid(True)
plt.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Show only every nth label to prevent overcrowding
n = 12  # Show every nth label
plt.xticks(mean.index[::n])

# Adjust layout to prevent label cutoff
plt.tight_layout()

plt.savefig('Figures/mean_energy_usage.png')
# Show the plot
plt.show()

