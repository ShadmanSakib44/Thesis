
import requests
import json
import pandas as pd

def get_response_from_server(prompt, model="phi4"): # llama2 is the model name for the Llama model
    # Define the URL for the POST request
    url = "http://localhost:11434/api/chat"
    
    # Payload for the POST request
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        # Send a POST request to the /api/chat endpoint with streaming enabled
        response = requests.post(url, json=payload, stream=True)
        
        # Check if the response status is OK
        if response.status_code == 200:
            complete_response = ""
            for line in response.iter_lines():
                if line:  # Ignore empty lines
                    try:
                        # Parse the JSON object
                        chunk = json.loads(line)
                        # Extract the "content" field and append it to the complete response
                        if "message" in chunk and "content" in chunk["message"]:
                            complete_response += chunk["message"]["content"]
                    except (KeyError, json.JSONDecodeError) as e:
                        # Handle cases where the line isn't valid JSON or lacks expected fields
                        print("Warning: Skipped a line due to error -", str(e), "Line:", line.decode("utf-8"))
            return complete_response
        else:
            # Handle error response status
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        # Handle any connection errors
        print("Error connecting to the server:", e)
        return None

def generate_user_stories(input_file, output_file):
    # Read the input Excel file
    df = pd.read_excel(input_file)
    
    # Check if 'review_content' column exists
    if 'review_content' not in df.columns:
        print("Error: 'review_content' column not found in the input file.")
        return
    
    # Create a list to store user stories
    user_stories = []
    
    # Iterate through each row and generate a user story for each review_content
    for index, row in df.iterrows():
        review_content = row['review_content']
        
        # Generate user story from review_content
        print(f"Generating user story for review {index + 1}...")
        user_story = get_response_from_server(f"Generate a user story for this review: {review_content}")
        
        if user_story:
            user_stories.append(user_story)
        else:
            user_stories.append("Error generating user story.")
    
    # Add the generated user stories to the DataFrame
    df['user_story'] = user_stories
    
    # Write the DataFrame with user stories to a new Excel file
    df.to_excel(output_file, index=False)
    print(f"User stories generated and saved to {output_file}")

# Input and output file paths
input_file = "trail1.xlsx"
output_file = "output_phi4_zero_shot.xlsx"

# Generate user stories from the reviews
generate_user_stories(input_file, output_file)

