import pandas as pd

# File paths
merged_path = "/Users/shadmansakib/Documents/Thesis/OLD/Dataset/merged_final.csv"
filtered_200_path = "/Users/shadmansakib/Desktop/filtered_200.csv"
output_path = "merged_first_1000.csv"

# Load datasets
merged_df = pd.read_csv(merged_path)
filtered_200_df = pd.read_csv(filtered_200_path).head(200)

# Get first 1000 rows from merged
first_1000_df = merged_df.head(1000)

# Save to new file
first_1000_df.to_csv(output_path, index=False)
print(f"Saved first 1000 rows to: {output_path}")

# Check if all 200 app_review values are in the new file
missing = filtered_200_df[~filtered_200_df['app_review'].isin(first_1000_df['app_review'])]

if missing.empty:
    print("✅ All 200 reviews from filtered_200.csv are present in merged_first_1000.csv.")
else:
    print(f"❌ {len(missing)} reviews from filtered_200.csv are missing in merged_first_1000.csv.")
