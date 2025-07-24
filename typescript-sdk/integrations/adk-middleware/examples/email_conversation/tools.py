from typing import Optional

# Static dictionary of user names and their corresponding emails
USER_EMAIL_MAP = {
    "Ayan Murad": "ayan.murad@aretec.ai",
    "James Schlauch": "james.schlauch@slamsports.ai",
    "Sara Akhtar": "sara.akhtar@aretec.ai",
    "James Schlauch": "james@slamsports.ai",
    "Ayan Murad": "aynoolroxx987@gmail.com",
    "Humayun Shakeel": "humayun.shakeel@aretec.ai",
    "Syed Fakher": "sfakher27@gmail.com",
    "Taha Rauf": "taha.rauf@aretec.ai",
    "waqas": "waqas@aretec.ai",
    "Muhammad Areeb": "muhammad.areeb@aretec.ai",
    "Eman Fatima": "eman.fatima@aretec.ai",
    "Cheryl John": "cheryl.john@aretec.ai",
    "Waqas Haq": "waqas.haq@slamsports.ai",
    "Barrett Stover": "barrett.stover@slamsports.ai",
    "Muhammad Areeb": "m.areebkhan125@gmail.com",
    "Waqas Haq": "waqas@datapulsetech.ai",
    "Justin Weiss": "justinweiss2023@gmail.com",
    "DC Arendas": "dc.arendas@gmail.com",
    "Samreen Habib": "samreen.habib@aretec.ai",
    "James Schlauch": "james@hiapply.co",
    "Elliott Barnes": "elliott@slamsports.ai",
    "Muqadas Ashraf": "muqadas.ashraf@aretec.ai",
    "James schlauch": "james.schlauch@aretecinc.com",
    "Fakher Uddin": "fakher.uddin@aretec.ai",
    "Syed Fakher": "fakher.uddin@aretecinc.com",
    "Ayan Murad": "ayanmuradahmed@gmail.com",
    "Niamat Khan": "niamat.khan@aretec.ai",
    "Huzaifa Ahmed": "huzaifa.ahmed@aretec.ai",
    "Waqasul Haq": "waqas@aretecinc.com",
    "Daniyal Zaidi": "daniyal.zaidi@aretec.ai",
    "Sahar Ali": "sahar.ali@aretec.ai",
    "Waqas Haq": "waqasulhaq2003@gmail.com",
    "Roby Luna": "roby@slamsports.ai",
    "Mike Roberts": "robsma6@gmail.com",
}

def fetch_email_by_name(name: str) -> Optional[str]:
    """
    Fetches the email address associated with a given name by searching
    the static USER_EMAIL_MAP for the best match.

    Args:
        name (str): The name to look up (case-insensitive).

    Returns:
        Optional[str]: The email address if found, otherwise None.
    """
    # Normalize the search name for case-insensitive comparison
    search_name_normalized = name.strip().lower()

    # Initialize variables for tracking the best match
    best_match_email = None
    best_match_full_name = None
    highest_match_score = 2  # Simple score: length of matched name part

    try:
        # Iterate through the static dictionary
        for full_name, email in USER_EMAIL_MAP.items():
            # Normalize full name for comparison
            full_name_normalized = full_name.lower()

            # --- Best Match Logic ---
            # Check if the search name is a substring of the full name
            if search_name_normalized in full_name_normalized:
                # Simple scoring: prefer longer matches or matches closer to the beginning?
                # For now, just use the length of the search term as a basic score
                # if it's found. This prioritizes finding the name part.
                match_score = len(search_name_normalized)

                # Update best match if this one scores higher
                # (This simple logic means the *last* equally good match will be chosen
                # if there are ties. You could make it more sophisticated).
                if match_score > highest_match_score:
                    highest_match_score = match_score
                    best_match_email = email
                    best_match_full_name = full_name
            # --- End Best Match Logic ---

        if best_match_email:
            print(f"✓ Found best matching email for '{name}': {best_match_email} ({best_match_full_name})")
            return best_match_email
        else:
            print(f"✗ No email found matching the name '{name}'.")
            return None

    except Exception as e:
        print(f"✗ Error searching for name '{name}': {e}")
        return None

# Example usage (if running the script directly)
if __name__ == "__main__":
    # Test cases
    test_names = ["samreen", "waqas", "james", "ayan", "nonexistent"]
    for test_name in test_names:
        print(f"\n--- Searching for: '{test_name}' ---")
        email = fetch_email_by_name(test_name)
        if email:
            print(f"Found: {email}")
        else:
            print("Not found.")