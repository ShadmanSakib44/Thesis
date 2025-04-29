import pandas as pd

# Load the CSV file
file_path = r'D:\Research\Thesis\OLD\Dataset\filtered.csv'
df = pd.read_csv(file_path)

# View a sample of the app column to understand values (optional)
# print(df['app'].unique())

# Count the occurrences of each app
app_counts = df['app'].value_counts()

# Filter counts for Samsung, Huawei, and Garmin
target_apps = ['Samsung', 'Huawei', 'Garmin']
filtered_counts = app_counts[app_counts.index.str.contains('|'.join(target_apps), case=False)]

# Calculate total and percentage
total_reviews = filtered_counts.sum()
distribution = (filtered_counts / total_reviews) * 100

# Display the results
print("Review Count:")
print(filtered_counts)
print("\nPercentage Distribution:")
print(distribution.round(2))
