import pandas as pd

# Load both CSVs
problem_reports = pd.read_csv("problem_reports.csv")
feature_requests = pd.read_csv("feature_requests.csv")

# Merge the two datasets
merged_labeled = pd.concat([problem_reports, feature_requests], ignore_index=True)

# Filter rows where 'data' has between 40 and 50 words
def is_ideal_length(text, min_words=25, max_words=50):
    if not isinstance(text, str):
        return False
    word_count = len(text.split())
    return min_words <= word_count <= max_words

merged_labeled = merged_labeled[merged_labeled['data'].apply(is_ideal_length)]

# Optional: Shuffle the filtered data
merged_labeled = merged_labeled.sample(frac=1, random_state=42).reset_index(drop=True)

# Save the filtered and merged dataset
merged_labeled.to_csv("filtered.csv", index=False)
