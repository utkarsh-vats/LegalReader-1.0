import os
import json
from google import genai

def translate_legal_jargon(raw_data):
    if not raw_data:
        return "No hearing history available to translate."
    
    client = genai.Client()
    prompt = f"""
    You are an expert Indian legal translator. Your job is to read the following raw JSON data from the eCourts system and summarize the latest hearing history in plain, easy-to-understand English.
    RULES:
        - Do not use legal jargon (e.g., translate "WS" to "Written Statement").
        - Keep the summary under 3 sentences.
        - Be direct and objective.
    Raw Data:
    {json.dumps(raw_data, indent=4)}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        if response.text:
            return response.text.strip()
        else:
            return f"Summary not available. (AI returned an empty response.)"

    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return "Could not generate a plain English summary at this time. Please try again later."