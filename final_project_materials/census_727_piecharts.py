import pandas as pd
import matplotlib.pyplot as plt

# Mockup data for demonstration (replace with your data for actual use)
data = {
    "region": ["Blue Wall", "South", "Sunbelt"],
    "percent_white": [70.5, 55.2, 63.8],
    "percent_black": [15.3, 32.1, 10.4],
    "percent_hispanic": [10.2, 8.7, 23.6],
}

# Convert the data into a DataFrame
df = pd.DataFrame(data)

# Prepare data for the plots
categories = ["percent_white", "percent_black", "percent_hispanic"]
colors = ['lightblue', 'lightcoral', 'gold']
labels = ["White", "Black", "Hispanic"]

# Create subplots for side-by-side comparison
fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

# Generate Pie Charts for Each Region
for i, ax in enumerate(axes):
    region_data = df.iloc[i, 1:]  # Percentages for the current region
    ax.pie(region_data, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax.set_title(df['region'][i])

# Set a main title
fig.suptitle("Racial Makeup by Region (Pie Charts)", fontsize=16)

# Show the pie charts
plt.tight_layout()
plt.show()

# Create Bar Chart for Comparison
fig, ax = plt.subplots(figsize=(10, 6))

# Pivot data for easier plotting
bar_data = df.set_index('region')[categories].T

# Create side-by-side bars
bar_data.plot(kind='bar', ax=ax, color=colors, width=0.8)

# Customize bar chart
ax.set_title("Racial Makeup Comparison Across Regions", fontsize=16)
ax.set_ylabel("Percentage")
ax.set_xlabel("Racial Categories")
ax.legend(title="Region", fontsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.7)

# Show the bar chart
plt.tight_layout()
plt.show()
