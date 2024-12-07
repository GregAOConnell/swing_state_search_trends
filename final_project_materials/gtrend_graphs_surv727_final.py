import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Load the combined dataset
file_path_combined = '/Users/gregoconnell/Documents/GitHub/APAN-hw/surv727-dataviz/final_pngs/combined_search_trends.csv'
combined_data = pd.read_csv(file_path_combined)

# Convert the 'date' column to datetime for proper plotting
combined_data['date'] = pd.to_datetime(combined_data['date'])

# Define state groups
state_groups = {
    "Sunbelt States": ["US-AZ", "US-NV"],
    "Southern States": ["US-NC", "US-GA"],
    "Blue Wall States": ["US-PA", "US-MI", "US-WI"]
}

# Set a color palette for better distinguishability
color_palette = sns.color_palette("tab10")
us_trend_color = 'black'  # Define a distinctive color for US-wide trends

# Function to plot trends for specific state group with US comparison
def plot_trends_with_us_comparison(data, keywords, state_group_name, states):
    for keyword in keywords:
        keyword_data = data[data['keyword'] == keyword]
        plt.figure(figsize=(10, 6))
        colors = iter(color_palette)  # Use color palette for state lines
        
        # Plot state-specific trends
        for state in states:
            state_data = keyword_data[keyword_data['state'] == state]
            if not state_data.empty:
                plt.plot(state_data['date'], state_data['hits'], label=state, color=next(colors))
        
        # Plot US-wide trends
        us_data = keyword_data[keyword_data['state'] == "US"]
        if not us_data.empty:
            plt.plot(us_data['date'], us_data['hits'], label="US (All States)", color=us_trend_color, linewidth=2, linestyle='--')
        
        # Formatting the plot
        plt.title(f"Search Trends for '{keyword}' in {state_group_name}")
        plt.xlabel('Date')
        plt.ylabel('Search Hits')
        plt.legend(title="State")
        plt.grid(True, linestyle='--', alpha=0.5)
        
        # Format the x-axis to show fewer ticks
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=30))  # One tick every 30 days
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gcf().autofmt_xdate()  # Auto-format date labels for better readability

        plt.tight_layout()
        
        # Save the plot as a PNG file
        file_name = f"{keyword}_{state_group_name.replace(' ', '_')}_with_us_comparison.png"
        plt.savefig(file_name, dpi=300)
        plt.show()

# Get the unique keywords from the dataset
keywords = combined_data['keyword'].unique()

# Plot trends for each state group with US comparison
for group_name, states in state_groups.items():
    plot_trends_with_us_comparison(combined_data, keywords, group_name, states)
    
    
    
#Percent diff
    import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Directory to save plots
output_dir = '/Users/gregoconnell/Documents/GitHub/APAN-hw/surv727-dataviz/final_pngs/'
os.makedirs(output_dir, exist_ok=True)

# Initialize list for keyword difference data
all_keyword_differences = []

# Calculate and plot percentage differences for all keywords
for keyword in combined_data['keyword'].unique():
    keyword_data = combined_data[combined_data['keyword'] == keyword]
    us_data = keyword_data[keyword_data['state'] == "US"].set_index("date")["hits"]
    state_data = keyword_data[keyword_data['state'] != "US"]
    
    if not us_data.empty and not state_data.empty:
        state_data = state_data.assign(
            pct_diff=lambda x: 100 * (x["hits"] - x["date"].map(us_data)) / x["date"].map(us_data)
        )
        # Replace NaN or Inf values with 0 for stability
        state_data['pct_diff'].replace([np.inf, -np.inf], np.nan, inplace=True)
        state_data['pct_diff'].fillna(0, inplace=True)
        all_keyword_differences.append(state_data)
        
        # Plot the percentage differences
        plt.figure(figsize=(12, 6))
        for state in state_data['state'].unique():
            sns.lineplot(data=state_data[state_data["state"] == state], x="date", y="pct_diff", label=state)
        
        plt.axhline(0, color="red", linestyle="--", label="US Baseline")
        plt.title(f"Percentage Difference from US Trends for '{keyword}'")
        plt.xlabel("Date")
        plt.ylabel("Percentage Difference (%)")
        plt.legend(title="State")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        
        # Save plot as PNG
        file_name = os.path.join(output_dir, f"{keyword.replace(' ', '_')}_percentage_diff.png")
        plt.savefig(file_name, dpi=300)
        plt.close()

# Combine all keyword differences for analysis
if all_keyword_differences:
    percentage_diff_data = pd.concat(all_keyword_differences, ignore_index=True)

    # Analyze overall percent differences and detect outliers
    summary_stats = percentage_diff_data.groupby('state')['pct_diff'].describe()
    outliers = percentage_diff_data[
        (percentage_diff_data['pct_diff'] > percentage_diff_data['pct_diff'].quantile(0.95)) | 
        (percentage_diff_data['pct_diff'] < percentage_diff_data['pct_diff'].quantile(0.05))
    ]

    # Save summary stats and outliers as CSVs for review
    summary_stats.to_csv('/Users/gregoconnell/Documents/GitHub/APAN-hw/surv727-dataviz/final_pngs/summary_percentage_diff.csv')
    outliers.to_csv('/Users/gregoconnell/Documents/GitHub/APAN-hw/surv727-dataviz/final_pngs/outliers_percentage_diff.csv')

    print("Summary statistics and outliers have been saved as CSV files.")
else:
    print("No valid percentage difference data to analyze.")

from scipy.stats import ttest_rel
import pandas as pd

# Function to perform paired t-tests
def perform_t_tests(data):
    results = []
    keywords = data['keyword'].unique()
    
    for keyword in keywords:
        keyword_data = data[data['keyword'] == keyword]
        us_data = keyword_data[keyword_data['state'] == "US"].set_index("date")["hits"]
        
        for state in keyword_data['state'].unique():
            if state == "US":
                continue
            
            state_data = keyword_data[keyword_data['state'] == state].set_index("date")["hits"]
            common_dates = state_data.index.intersection(us_data.index)
            
            # Only compare if there are overlapping dates
            if len(common_dates) > 1:
                t_stat, p_value = ttest_rel(state_data.loc[common_dates], us_data.loc[common_dates])
                results.append({
                    "keyword": keyword,
                    "state": state,
                    "t_stat": t_stat,
                    "p_value": p_value,
                    "significant": p_value < 0.05
                })
    
    return pd.DataFrame(results)

# Perform t-tests
try:
    t_test_results = perform_t_tests(combined_data)
except Exception as e:
    print(f"Error while performing t-tests: {e}")
    t_test_results = None

# Save results to CSV if available
if t_test_results is not None:
    output_csv = '/Users/gregoconnell/Documents/GitHub/APAN-hw/surv727-dataviz/final_pngs/t_test_results.csv'
    t_test_results.to_csv(output_csv, index=False)
    print(f"T-test results saved to {output_csv}")
else:
    print("No t-test results available.")
    
    
    import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define state groups
state_groups = {
    "Sunbelt States": ["US-AZ", "US-NV"],
    "Southern States": ["US-NC", "US-GA"],
    "Blue Wall States": ["US-PA", "US-MI", "US-WI"]
}

# Create output directory for line graphs
output_dir = '/Users/gregoconnell/Documents/GitHub/APAN-hw/surv727-dataviz/final_pngs/'
os.makedirs(output_dir, exist_ok=True)

# Function to calculate percentage differences and plot grouped lines
def plot_grouped_percentage_diff(data, keyword, save_path):
    keyword_data = data[data['keyword'] == keyword]
    us_data = keyword_data[keyword_data['state'] == "US"].set_index("date")["hits"]
    group_diffs = []

    plt.figure(figsize=(12, 6))
    for group_name, states in state_groups.items():
        group_data = keyword_data[keyword_data['state'].isin(states)]
        if not group_data.empty and not us_data.empty:
            group_data = group_data.assign(
                pct_diff=lambda x: 100 * (x["hits"] - x["date"].map(us_data)) / x["date"].map(us_data)
            )
            group_mean = group_data.groupby("date")["pct_diff"].mean()
            sns.lineplot(data=group_mean, label=group_name)
            group_diffs.append(group_mean)
    
    # Add baseline
    plt.axhline(0, color="red", linestyle="--", label="US Baseline")
    plt.title(f"Percentage Differences from US Trends for '{keyword}'")
    plt.xlabel("Date")
    plt.ylabel("Percentage Difference (%)")
    plt.legend(title="State Group")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    
    # Save plot as PNG
    file_name = os.path.join(save_path, f"{keyword.replace(' ', '_')}_grouped_percentage_diff.png")
    plt.savefig(file_name, dpi=300)
    plt.close()

# Plot percentage differences for each keyword grouped by state groups
for keyword in combined_data['keyword'].unique():
    plot_grouped_percentage_diff(combined_data, keyword, output_dir)

print(f"Plots have been saved in {output_dir}")


# Function to calculate percentage differences for all states combined and plot
def plot_combined_percentage_diff(data, keyword, save_path):
    keyword_data = data[data['keyword'] == keyword]
    us_data = keyword_data[keyword_data['state'] == "US"].set_index("date")["hits"]
    
    # Combine all states into one group
    all_states_data = keyword_data[keyword_data['state'] != "US"]
    if not all_states_data.empty and not us_data.empty:
        all_states_data = all_states_data.assign(
            pct_diff=lambda x: 100 * (x["hits"] - x["date"].map(us_data)) / x["date"].map(us_data)
        )
        combined_states_diff = all_states_data.groupby("date")["pct_diff"].mean()
        
        # Plot
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=combined_states_diff, label="All States Combined", color="blue")
        plt.axhline(0, color="red", linestyle="--", label="US Baseline")
        plt.title(f"Combined States vs. US Percentage Differences for '{keyword}'")
        plt.xlabel("Date")
        plt.ylabel("Percentage Difference (%)")
        plt.legend(title="Comparison")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        
        # Save plot as PNG
        file_name = os.path.join(save_path, f"{keyword.replace(' ', '_')}_combined_states_diff.png")
        plt.savefig(file_name, dpi=300)
        plt.close()

# Create output directory for combined plots
combined_output_dir = '/Users/gregoconnell/Documents/GitHub/APAN-hw/surv727-dataviz/final_pngs/'
os.makedirs(combined_output_dir, exist_ok=True)

# Plot percentage differences for each keyword with all states combined
for keyword in combined_data['keyword'].unique():
    plot_combined_percentage_diff(combined_data, keyword, combined_output_dir)

print(f"Combined state comparison plots have been saved in {combined_output_dir}")
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load the CSV file
file_path = '/Users/gregoconnell/Documents/GitHub/APAN-hw/surv727-dataviz/final_pngs/t_test_results.csv'  # Replace with your actual file path
data = pd.read_csv(file_path)
# Filter out the "migrant crime" keyword
data = data[data['keyword'] != 'migrant crime']

# Create categories for counting states
data['category'] = data.apply(
    lambda row: 'Positive' if row['t_stat'] > 0 and row['significant']
    else 'Negative' if row['t_stat'] < 0 and row['significant']
    else 'Non-Significant',
    axis=1
)

# Define a consistent color mapping and legend order
color_mapping = {'Positive': '#77DD77', 'Negative': '#FFB347', 'Non-Significant': '#89CFF0'}
legend_order = ['Positive', 'Negative', 'Non-Significant']

# ---- Plot 1: Count of States ----
# Group by keyword and category, count the states
state_counts = data.groupby(['keyword', 'category']).size().unstack(fill_value=0)

# Plot the count of states
fig, ax = plt.subplots(figsize=(12, 8))
bars = state_counts[legend_order].plot(
    kind='bar', 
    stacked=True, 
    color=[color_mapping[c] for c in legend_order], 
    ax=ax
)

# Manually create legend to ensure consistent order
handles = [plt.Rectangle((0, 0), 1, 1, color=color_mapping[category]) for category in legend_order]
ax.legend(handles, legend_order, title="Category", fontsize=10)

# Add title and labels
ax.set_title("Count of States with Positive, Negative, or Non-Significant T-Values", fontsize=16)
ax.set_xlabel("Keyword")
ax.set_ylabel("Number of States")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# ---- Plot 2: Strength of T-Values ----
# Create a pivot table for the strength of t-values
t_value_strength = data.pivot_table(
    index='keyword',
    columns='category',
    values='t_stat',
    aggfunc='mean',
    fill_value=0
)

# Reorder columns for consistent legend order
t_value_strength = t_value_strength[legend_order]

# Plot the strength of t-values
fig, ax = plt.subplots(figsize=(12, 8))
bar_width = 0.25
positions = np.arange(len(t_value_strength.index))

# Plot each category
for i, category in enumerate(legend_order):
    ax.bar(
        positions + i * bar_width,
        t_value_strength[category],
        bar_width,
        label=category,
        color=color_mapping[category]
    )

# Add labels and formatting
ax.set_xticks(positions + bar_width)
ax.set_xticklabels(t_value_strength.index, rotation=45, ha='right')
ax.set_title("Average Strength of T-Values by Keyword", fontsize=16)
ax.set_xlabel("Keyword")
ax.set_ylabel("Average T-Value")
ax.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.7)  # Horizontal line at 0

# Manually create legend for consistent order
handles = [plt.Rectangle((0, 0), 1, 1, color=color_mapping[category]) for category in legend_order]
ax.legend(handles, legend_order, title="Category", fontsize=10)

plt.tight_layout()
plt.show()
