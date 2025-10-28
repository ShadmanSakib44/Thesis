# import pandas as pd

# # Load both CSVs
# problem_reports = pd.read_csv("problem_reports.csv")
# feature_requests = pd.read_csv("feature_requests.csv")

# # Merge the two datasets
# merged_labeled = pd.concat([problem_reports, feature_requests], ignore_index=True)

# # Filter rows where 'data' has between 40 and 50 words
# def is_ideal_length(text, min_words=25, max_words=50):
#     if not isinstance(text, str):
#         return False
#     word_count = len(text.split())
#     return min_words <= word_count <= max_words

# merged_labeled = merged_labeled[merged_labeled['data'].apply(is_ideal_length)]

# # Optional: Shuffle the filtered data
# merged_labeled = merged_labeled.sample(frac=1, random_state=42).reset_index(drop=True)

# # Save the filtered and merged dataset
# merged_labeled.to_csv("filtered.csv", index=False)


import pandas as pd

# Load the first 200 rows (fixed set)
file1_path = "/Users/shadmansakib/Desktop/filtered_200.csv"
df1 = pd.read_csv(file1_path).head(200)

# Load all rows from second file
file2_path = "/Users/shadmansakib/Documents/Thesis/OLD/Dataset/app_reviews_combined.csv"
df2 = pd.read_csv(file2_path)

# Filter df2: remove rows with duplicate 'app_review' found in df1
filtered_df2 = df2[~df2['app_review'].isin(df1['app_review'])]

# Combine both, keeping df1 intact
merged_df = pd.concat([df1, filtered_df2], ignore_index=True)

# Save final merged result
output_path = "merged_final.csv"
merged_df.to_csv(output_path, index=False)

# Print final row count
print(f"Final row count (first 200 kept, rest deduplicated): {len(merged_df)}")
