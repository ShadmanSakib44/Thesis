import pandas as pd
import re

# Step 1: Merge the three CSV files
files = [
    "Samsung Health.en.csv",
    "Huawei Health.en.csv",
    "Garmin Connect.en.csv"
]

dfs = [pd.read_csv(file) for file in files]
merged_df = pd.concat(dfs, ignore_index=True)

# Step 2: Remove emojis from 'data'
def remove_emoji(text):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub('', str(text))

merged_df['data'] = merged_df['data'].astype(str).apply(remove_emoji)

# Step 3: Filter based on review word count
def is_reasonable_length(text, min_words=10, max_words=50):
    word_count = len(text.split())
    return min_words <= word_count <= max_words

merged_df = merged_df[merged_df['data'].apply(is_reasonable_length)].reset_index(drop=True)

# Step 4: Separate into problem reports and feature requests
problem_reports = merged_df[merged_df['problem_report'] == 1][['data', 'app']].copy()
problem_reports['type'] = 'problem_report'

feature_requests = merged_df[merged_df['feature_request'] == 1][['data', 'app']].copy()
feature_requests['type'] = 'feature_request'

# Step 5: Save outputs
problem_reports.to_csv("problem_reports.csv", index=False)
feature_requests.to_csv("feature_requests.csv", index=False)
