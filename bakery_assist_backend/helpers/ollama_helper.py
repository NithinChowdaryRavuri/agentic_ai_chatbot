import requests
import json
import re # For parsing the function call tag

def call_ollama(prompt):
    """Sends a prompt to the Ollama API (/api/chat) and returns the response content."""
    # Set up the base URL for the local Ollama API
    url = "http://localhost:11434/api/chat" # Using the chat endpoint

    # Structure for the /api/chat endpoint
    payload = {
        "model": "deepseek-r1", # Make sure this model is running in Ollama
        "messages": [{"role": "user", "content": prompt}],
        "stream": False # Get the full response at once
        # Add options if needed, e.g., "options": {"temperature": 0.2}
    }

    print(f"\n--- Sending Prompt to Ollama ({payload['model']}) ---")
    # print(prompt) # Uncomment to debug the exact prompt being sent
    print("--- End Prompt ---")

    try:
        # Consider adding a timeout (e.g., timeout=60 for 60 seconds)
        response = requests.post(url, json=payload, timeout=90)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        response_data = response.json()

        # --- CORRECT PARSING for /api/chat ---
        message_data = response_data.get("message", {})
        content = message_data.get("content", "").strip()
        # --- End Correction ---

        #print(f"\n--- Received Response from Ollama ---")
        # print(f"Raw Response Data: {response_data}") # Uncomment for deeper debugging
        #print(f"Extracted Content: {content}")
        #print("--- End Response ---")

        # Check if content is empty, which might indicate an issue
        if not content:
            print("Warning: Received empty content from Ollama.")
            # You might want to return None or a specific error message string here
            # return None
            
        return content

    except requests.exceptions.Timeout:
        print(f"Error: Ollama API request timed out.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding Ollama JSON response: {e}")
        print(f"Raw response text: {response.text}")
        return None

def parse_function_call(response_content):
    """
    Parses the LLM response to find a <function_call> tag and extracts
    the JSON object contained within it, even if extra text is present.
    Returns a dictionary with 'name' and 'arguments' if found, otherwise None.
    """
    print(f"\n--- Debug: Entering parse_function_call ---") # DEBUG
    print(f"Input type: {type(response_content)}") # DEBUG

    if not isinstance(response_content, str):
        print(f"Warning: parse_function_call received non-string input: {type(response_content)}")
        return None

    # 1. Find the block between <function_call> and </function_call>
    outer_match = re.search(r"<function_call>(.*?)</function_call>", response_content, re.DOTALL | re.IGNORECASE)
    print(f"Outer regex match object: {outer_match}") # DEBUG

    if outer_match:
        content_between_tags = outer_match.group(1).strip()
        print(f"Content between tags (raw): '{content_between_tags}'") # DEBUG

        # 2. Find the JSON object within that block
        # Look for the first '{' and the last '}'
        json_match = re.search(r"\{.*\}", content_between_tags, re.DOTALL)

        if json_match:
            json_str = json_match.group(0).strip() # group(0) is the whole match
            print(f"Potential JSON string found: '{json_str}'") # DEBUG

            # Optional: Basic cleanup for markdown fences around the extracted JSON
            if json_str.startswith("```json"): json_str = json_str[7:]
            if json_str.startswith("```"): json_str = json_str[3:]
            if json_str.endswith("```"): json_str = json_str[:-3]
            json_str = json_str.strip()
            print(f"Potential JSON string (cleaned): '{json_str}'") # DEBUG

            try:
                # 3. Attempt to parse the potential JSON
                call_data = json.loads(json_str)
                print(f"Successfully parsed JSON: {type(call_data)}") # DEBUG

                # 4. Validate the structure
                if isinstance(call_data, dict) and "name" in call_data and "arguments" in call_data:
                     print(f"--- Parsed Function Call ---")
                     print(json.dumps(call_data, indent=2))
                     print("--- End Parsed Call ---")
                     return call_data # Success!
                else:
                     print(f"Warning: Parsed JSON is not in the expected format: {call_data}") # DEBUG
                     return None
            except json.JSONDecodeError as e:
                # Failed to parse the extracted JSON string
                print(f"!!! Error decoding potential JSON string: {e} !!!") # DEBUG
                print(f"String attempted to parse: '{json_str}'") # DEBUG
                return None
        else:
            # Could not find '{...}' within the function call tags
            print("Debug: No JSON object ('{...}') found within the <function_call> tags.") # DEBUG
            return None
    else:
        # The outer <function_call> tags were not found
         print("Debug: No <function_call> tag found in response.") # DEBUG
         return None

    # Fallback return None
    return None