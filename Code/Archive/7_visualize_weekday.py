import pandas as pd 
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('Data/TL_data.csv')

# Convert start column to datetime
df['start'] = pd.to_datetime(df['start'])

# Extract day of week from start datetime
df['weekday'] = df['start'].dt.day_name()

# Extract hour and minute from datetime for grouping
df['time'] = df['start'].dt.strftime('%H:%M')



# Group by time and weekday to get mean values
grouped = df.groupby(['time', 'weekday'])['quantity_value-6060'].mean().unstack()

# Create the plot
plt.figure(figsize=(12, 6))

# Plot a line for each weekday
# Define weekday order
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
for weekday in weekday_order:
    plt.plot(grouped.index, grouped[weekday], label=weekday)

# Customize the plot
plt.title('Average Energy Usage by Day of Week')
plt.xlabel('Time of Day')
plt.ylabel('Energy Value')
plt.grid(True)
plt.legend()

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Show only every nth label to prevent overcrowding
n = 12  # Show every nth label
plt.xticks(grouped.index[::n])

# Adjust layout to prevent label cutoff
plt.tight_layout()

plt.savefig('Figures/weekday_energy_usage.png')
plt.show()
