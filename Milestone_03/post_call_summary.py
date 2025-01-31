import google.generativeai as genai
import pandas as pd
import re

def analyze_call_and_generate_summary(call_text, phone_number, crm_excel_path, api_key, model_name="gemini-pro"):
    """
    Analyze the call text and generate a post-call summary.

    Args:
        call_text (str): Text containing the call details.
        phone_number (str): Phone number to identify the contact in the CRM.
        crm_excel_path (str): Path to the CRM data Excel file.
        api_key (str): Gemini API key.
        model_name (str): The name of the Gemini model to use. Defaults to "gemini-pro".

    Returns:
        str: Post-call summary or error message.
    """
    # Configure Gemini API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)

    try:
        # Load CRM data
        crm_df = pd.read_excel(crm_excel_path)

        # Match the contact using the phone number
        crm_df["phone_number"] = crm_df["phone_number"].astype(str).str.strip()  # Clean phone numbers
        contact_row = crm_df[crm_df["phone_number"] == str(phone_number)]

        if contact_row.empty:
            return "Error: No matching contact found for the provided phone number."

        # Prepare the prompt for extraction
        prompt = f"""
        Analyze this call text and provide:
        Key Discussions and summary.
        Call Text: {call_text}
        """
        
        extraction_response = model.generate_content(prompt)

        # Debugging: Print the raw API response
        print("Gemini API Response:", extraction_response.text)

        response_text = extraction_response.text.strip()

        if not response_text:
            return "Error: The response from the Gemini API is empty."

        # Use regular expressions to extract key discussions and intent
        key_discussions_match = re.search(r"Key Discussions:\s*\* (.*)", response_text, re.DOTALL)
        intent_match = re.search(r"Summary:\s*\* (.*)", response_text, re.DOTALL)

        if key_discussions_match and intent_match:
            # Extract the matched groups
            key_discussions = key_discussions_match.group(1).strip()
            intent = intent_match.group(1).strip()

            # Create a concise summary
            summary = f"The customer discussed {key_discussions}. The post call summary generated {summary}."
            return summary
        else:
            return "Error: Could not parse the key discussions and summary from the response."

    except Exception as e:
        return f"Error: {e}"

# Example usage
if _name_ == "_main_":
    # Replace with your actual call details and API key
    sample_call_text = "The product needs improvements in its UI and UX, especially for better navigation."
    sample_phone_number = "001-431-560-3386"
    crm_data_path = r"C:\Users\shriy\OneDrive\Desktop\salesassistant1\crm_data.xlsx"  # Use raw string for the file path
    gemini_api_key = "AIzaSyD_Yg_YrRQ9hVggBlnSq7zgbF9kYilPo_A"  # Replace with your API key

    result = analyze_call_and_generate_summary(sample_call_text, sample_phone_number, crm_data_path, gemini_api_key)
    print(result)
