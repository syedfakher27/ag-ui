from typing import Optional, Dict

# Mock database of users (in real usage, this might come from an API or DB)
USER_EMAIL_MAP = {
    "samreen": "samreen.habib@aretec.ai",
}

def fetch_email_by_name(name: str) -> Optional[str]:
    """
    Fetches the email address associated with a given name.
    
    Args:
        name (str): The name to look up (case-insensitive).
        
    Returns:
        Optional[str]: The email address if found, otherwise None.
    """
    # Normalize the name to lowercase for case-insensitive matching
    normalized_name = name.lower().strip()
    
    # Look up the email in the mock map
    email = USER_EMAIL_MAP.get(normalized_name)
    
    if email:
        print(f"✓ Found email for '{name}': {email}")
    else:
        print(f"✗ No email found for '{name}'")
    
    return email


if __name__ == "__main__":
    # Simulate user query parsing
    user_query = "send this conversation to samreen"
    
    # Extract name from query (basic example using split)
    words = user_query.split()
    if "to" in words:
        try:
            name_index = words.index("to") + 1
            recipient_name = words[name_index]
            
            # Now fetch the email
            recipient_email = fetch_email_by_name(recipient_name)
            
            if recipient_email:
                print(f"You can now send the email to: {recipient_email}")
            else:
                print("Unable to find the recipient's email.")
        except IndexError:
            print("Could not extract the recipient's name.")
    else:
        print("No recipient specified in the query.")