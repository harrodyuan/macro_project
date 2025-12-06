import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_theme(style="darkgrid")
plt.rcParams['figure.figsize'] = (14, 10)

def plot_intraday(ax, df, date, title, yield_col='2Y_Yield', color='blue'):
    day_data = df[df['Date'] == date].sort_values('Datetime')
    # Filter 8:00 to 12:00
    day_data = day_data[(day_data['Datetime'].dt.hour >= 8) & (day_data['Datetime'].dt.hour < 12)]
    
    ax.plot(day_data['Datetime'], day_data[yield_col], label=yield_col.replace('_', ' '), color=color, linewidth=2)
    
    # Release line
    release_time = pd.Timestamp(f"{date} 08:30:00")
    ax.axvline(release_time, color='red', linestyle='--', alpha=0.7, label='Release (8:30)')
    
    # Get actual/surveyed for title
    actual = day_data['Actual'].iloc[0]
    surveyed = day_data['Surveyed'].iloc[0]
    
    ax.set_title(f"{title}\nDate: {date} | Act: {actual} vs Surv: {surveyed}", fontsize=12)
    ax.legend(loc='upper left')
    ax.tick_params(axis='x', rotation=45)

def generate_event_comparison():
    print("Generating Event Comparison...")
    cpi_df = pd.read_csv('cleaned_cpi_data.csv')
    unemp_df = pd.read_csv('cleaned_unemployment_data.csv')
    
    cpi_df['Datetime'] = pd.to_datetime(cpi_df['Datetime'])
    unemp_df['Datetime'] = pd.to_datetime(unemp_df['Datetime'])
    
    # Find interesting dates
    cpi_date = '2024-01-11' 
    
    # Find max surprise for Unemployment
    unemp_df['Surprise'] = abs(unemp_df['Actual'] - unemp_df['Surveyed'])
    unemp_date = unemp_df.sort_values('Surprise', ascending=False)['Date'].iloc[0]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # Top Row: CPI
    plot_intraday(axes[0, 0], cpi_df, cpi_date, "CPI - 2 Year Yield", '2Y_Yield', 'royalblue')
    plot_intraday(axes[0, 1], cpi_df, cpi_date, "CPI - 10 Year Yield", '10Y_Yield', 'navy')
    
    # Bottom Row: Unemployment
    plot_intraday(axes[1, 0], unemp_df, unemp_date, "Unemployment - 2 Year Yield", '2Y_Yield', 'forestgreen')
    plot_intraday(axes[1, 1], unemp_df, unemp_date, "Unemployment - 10 Year Yield", '10Y_Yield', 'darkgreen')
    
    plt.tight_layout()
    plt.savefig('readme_event_comparison.png')
    print("Saved readme_event_comparison.png")

def run_strategy(df, event_name, threshold=0.0):
    trades = []
    df['Time_Component'] = df['Datetime'].dt.time
    unique_dates = df['Date'].unique()
    
    for date in unique_dates:
        day_data = df[df['Date'] == date].sort_values('Datetime')
        if day_data.empty: continue
        
        actual = day_data['Actual'].iloc[0]
        surveyed = day_data['Surveyed'].iloc[0]
        
        if abs(actual - surveyed) < threshold: continue
        
        bias = 0
        if event_name == 'CPI':
            if actual > surveyed: bias = 1
            elif actual < surveyed: bias = -1
        elif event_name == 'Unemployment':
            if actual > surveyed: bias = -1
            elif actual < surveyed: bias = 1
            
        if bias == 0: continue
        
        entry_candidates = day_data[day_data['Time_Component'] >= pd.to_datetime('09:00:00').time()]
        if entry_candidates.empty: continue
        
        entry_row = entry_candidates.iloc[0]
        exit_row = day_data.iloc[-1]
        
        # Reversion PnL
        pnl_2y = -1 * bias * (exit_row['2Y_Yield'] - entry_row['2Y_Yield'])
        pnl_10y = -1 * bias * (exit_row['10Y_Yield'] - entry_row['10Y_Yield'])
        
        trades.append({'Date': date, 'PnL_2Y': pnl_2y, 'PnL_10Y': pnl_10y})
        
    res_df = pd.DataFrame(trades)
    if not res_df.empty:
        res_df['Date'] = pd.to_datetime(res_df['Date'])
        res_df = res_df.sort_values('Date').reset_index(drop=True)
    return res_df

def generate_optimization_comparison():
    print("Generating Optimization Comparison...")
    cpi_df = pd.read_csv('cleaned_cpi_data.csv')
    unemp_df = pd.read_csv('cleaned_unemployment_data.csv')
    
    cpi_df['Datetime'] = pd.to_datetime(cpi_df['Datetime'])
    unemp_df['Datetime'] = pd.to_datetime(unemp_df['Datetime'])
    
    # Run Strategies
    # 1. Unfiltered (Threshold = 0.0)
    cpi_unfiltered = run_strategy(cpi_df, 'CPI', threshold=0.0)
    unemp_unfiltered = run_strategy(unemp_df, 'Unemployment', threshold=0.0)
    
    # 2. Filtered (Threshold = 0.001 / 0.1%)
    cpi_filtered = run_strategy(cpi_df, 'CPI', threshold=0.001)
    unemp_filtered = run_strategy(unemp_df, 'Unemployment', threshold=0.001)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # CPI Plot
    if not cpi_unfiltered.empty:
        cpi_unfiltered['Cum_2Y'] = cpi_unfiltered['PnL_2Y'].cumsum()
        # Use step plot for accurate PnL representation
        axes[0].step(cpi_unfiltered['Date'], cpi_unfiltered['Cum_2Y'], where='post', label='Unfiltered (All Trades)', color='gray', alpha=0.6)
        
    if not cpi_filtered.empty:
        cpi_filtered['Cum_2Y'] = cpi_filtered['PnL_2Y'].cumsum()
        axes[0].step(cpi_filtered['Date'], cpi_filtered['Cum_2Y'], where='post', label='Filtered (>0.1% Surprise)', color='blue', linewidth=2)
        
    axes[0].set_title('CPI Strategy Optimization (2Y Yield)', fontsize=14)
    axes[0].axhline(0, color='black', linestyle=':', alpha=0.5)
    axes[0].set_ylabel('Cumulative Yield Capture')
    axes[0].legend()
    
    # Unemployment Plot
    if not unemp_unfiltered.empty:
        unemp_unfiltered['Cum_2Y'] = unemp_unfiltered['PnL_2Y'].cumsum()
        axes[1].step(unemp_unfiltered['Date'], unemp_unfiltered['Cum_2Y'], where='post', label='Unfiltered (All Trades)', color='gray', alpha=0.6)
        
    if not unemp_filtered.empty:
        unemp_filtered['Cum_2Y'] = unemp_filtered['PnL_2Y'].cumsum()
        axes[1].step(unemp_filtered['Date'], unemp_filtered['Cum_2Y'], where='post', label='Filtered (>0.1% Surprise)', color='green', linewidth=2)
        
    axes[1].set_title('Unemployment Strategy Optimization (2Y Yield)', fontsize=14)
    axes[1].axhline(0, color='black', linestyle=':', alpha=0.5)
    axes[1].set_ylabel('Cumulative Yield Capture')
    axes[1].legend()
        
    plt.tight_layout()
    plt.savefig('readme_optimization_comparison.png')
    print("Saved readme_optimization_comparison.png")

if __name__ == "__main__":
    generate_event_comparison()
    generate_optimization_comparison()
