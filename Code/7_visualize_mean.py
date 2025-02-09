import pandas as pd
import matplotlib.pyplot as plt

def load_and_process_data():
    # Load data
    df = pd.read_csv('Data/quantity_data.csv')
    
    # Convert start column to datetime and extract time
    df['start'] = pd.to_datetime(df['start'])
    df['time'] = df['start'].dt.strftime('%H:%M')
    
    return df

def calculate_statistics(df):
    # Group by time and calculate statistics
    grouped = df.groupby('time')['quantity_value-6060']
    mean = grouped.mean()
    std = grouped.std()
    
    return mean, std

def create_plot(mean, std):
    # Create figure
    fig = plt.figure(figsize=(12, 6))
    
    # Plot mean and standard deviation
    plt.plot(mean.index, mean.values, 'b-', label='Mean Energy Usage')
    plt.fill_between(mean.index,
                    mean.values - std,
                    mean.values + std,
                    color='b', alpha=0.1, label='±1 Standard Deviation')

    # Customize plot
    plt.title('Mean Daily Energy Usage with ±1 Standard Deviation')
    plt.xlabel('Time of Day')
    plt.ylabel('Energy Value')
    plt.grid(True)
    plt.legend()

    # Format x-axis
    plt.xticks(rotation=45)
    n = 12  # Show every nth label
    plt.xticks(mean.index[::n])

    # Adjust layout
    plt.tight_layout()
    
    return fig

def main():
    # Load and process data
    df = load_and_process_data()
    
    # Calculate statistics
    mean, std = calculate_statistics(df)
    
    # Create and save plot
    fig = create_plot(mean, std)
    fig.savefig('Figures/mean_energy_usage.png')
    plt.show()
    plt.close(fig)

if __name__ == "__main__":
    main()
