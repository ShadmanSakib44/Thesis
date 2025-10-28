import pandas as pd
import re

def count_tokens(text):
    """
    Counts tokens in a text based on splitting by spaces and punctuation.
    """
    if pd.isna(text):
        return 0
    # Split by non-word characters
    tokens = re.findall(r'\w+', text)
    return len(tokens)

def calculate_tokens_in_csv(input_file, text_column, output_file):
    # Load the CSV
    df = pd.read_csv(input_file)
    
    if text_column not in df.columns:
        print(f"Error: Column '{text_column}' not found in the file.")
        return
    
    # Count tokens for each entry in the specified column
    df['token_count'] = df[text_column].apply(count_tokens)
    
    # Save the token counts to a new file
    df.to_csv(output_file, index=False)
    print(f"Token counts calculated and saved to {output_file}.")
    
    # Print total token count
    total_tokens = df['token_count'].sum()
    print(f"Total tokens in the file: {total_tokens}")

# Input parameters
input_file = "cleaned_sampled_reviews.csv"  # Path to your CSV file
text_column = "review_content"  # Name of the column containing text
output_file = "tokenized_reviews.csv"  # Path to save the output file

# Calculate tokens
calculate_tokens_in_csv(input_file, text_column, output_file)
