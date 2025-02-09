import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm

# Create the plot
def plot_day(df_day, title):
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    
    ax.plot(df_day['start'], df_day['quantity_value-6060'])

    quality_filter = df_day['quantity_qualifier-6063'] == '220'
    x = df_day[quality_filter]['start']
    y= df_day[quality_filter]['quantity_value-6060']
    ax.scatter(x,y, color='blue',label='true value (220)', zorder=3)

    quality_filter = df_day['quantity_qualifier-6063'] == '67'
    x = df_day[quality_filter]['start']
    y = df_day[quality_filter]['quantity_value-6060']
    ax.scatter(x,y, color='green',label='replacement value (67)', zorder=3)

    quality_filter = df_day['quantity_qualifier-6063'] == 'Z18'
    x = df_day[quality_filter]['start']
    y = df_day[quality_filter]['quantity_value-6060']
    ax.scatter(x,y, color='red',label='preliminary value (Z18)', zorder=3)
    
    # Customize the plot
    ax.set_title(f'Energy Values for {title}')
    ax.set_xlabel('Time')
    
    ax.set_ylim(-0.5, 15)
    ax.set_ylabel('Energy Value [kWh]')
    ax.grid(True)
    ax.legend()

    # Rotate x-axis labels for better readability
    ax.tick_params(axis='x', rotation=45)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    return fig

def process_day(df, day, save_path):
            title = f'day {day}'
            df_day = df[df['start'].dt.date == day]
            df_day.sort_values(by='start', inplace=True)
            fig = plot_day(df_day, title)
            fig.savefig(f'{save_path}/{title}.png')
            plt.close(fig)

def process_and_plot_days(df, save_path='Figures'):
        df['start'] = pd.to_datetime(df['start'])
        df['end'] = pd.to_datetime(df['end'])
        # Filter for a single day (using the second day in the dataset)
        days = df['start'].dt.date.unique()
        for day in tqdm(days):
            process_day(df, day, save_path)

if __name__ == "__main__":
    df = pd.read_csv('Data/Aggregated_data.csv')
    process_and_plot_days(df)