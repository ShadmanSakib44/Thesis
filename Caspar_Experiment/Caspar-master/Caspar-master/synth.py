import csv

def load_event_pairs(filepath):
    """
    Reads synthesized event pairs from a CSV file.
    Each row is expected to have six columns:
    [Action_EID, Action_SID, Action_Text, Problem_EID, Problem_SID, Problem_Text]
    """
    event_pairs = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == 6:
                event_pairs.append(row)
            else:
                print("Skipping row with unexpected format:", row)
    return event_pairs

def synthesize_reviews(event_pairs):
    """
    For each event pair, create:
      - User review: concatenation of the user action text and the app problem text
      - User story: the app problem text only
    """
    synthesized = []
    for row in event_pairs:
        # Expecting: [action_EID, action_SID, action_text, problem_EID, problem_SID, problem_text]
        action_text = row[2].strip()
        problem_text = row[5].strip()
        user_review = action_text + " " + problem_text
        user_story = problem_text
        synthesized.append([user_review, user_story])
    return synthesized

def save_synthesized_reviews(synthesized, output_filepath):
    """
    Saves the synthesized reviews to a CSV file with two columns:
    "User review" and "User story"
    """
    with open(output_filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["User review", "User story"])
        writer.writerows(synthesized)

if __name__ == '__main__':
    input_filepath = 'data/eventpairs.csv'  # This file is assumed to be produced by the synthesis technique
    output_filepath = 'data/synthesized_reviews_final.csv'
    
    # Load the event pairs
    event_pairs = load_event_pairs(input_filepath)
    print(f"Loaded {len(event_pairs)} event pairs from {input_filepath}")
    
    # Synthesize the reviews (combine action and problem text)
    synthesized = synthesize_reviews(event_pairs)
    
    # Save the final synthesized reviews with two columns
    save_synthesized_reviews(synthesized, output_filepath)
    print("Synthesized reviews saved to:", output_filepath)
