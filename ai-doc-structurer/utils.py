import google.generativeai as genai
import pandas as pd
import pypdf
import json
import re

def extract_text_from_pdf(uploaded_file):
    """
    Extracts raw text from an uploaded PDF file object.
    """
    try:
        reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF: {e}")

def process_text_with_gemini(api_key, input_text):
    """
    Sends the text to Gemini to extract structured Key-Value-Comment data.
    """
    genai.configure(api_key=api_key)
    
    # Using the flash model for speed and efficiency
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Prompt Engineering:
    # 1. We strictly define the JSON structure.
    # 2. We explicitly tell it to split lists (like Certifications) into separate numbered keys.
    # 3. We instruct it to keep 'Comments' as original text from the source.
    prompt = f"""
    You are an expert Data Extraction AI. Your task is to convert unstructured text into a structured Excel-ready format.
    
    Input Text:
    {input_text}

    Directives:
    1. Extract ALL factual information as Key-Value pairs.
    2. Detect 'Comments' or 'Context' for each key. This MUST be the original sentence or phrase from the text that explains the fact.
    3. If there are multiple items in a category (e.g., Certifications, Projects, History), split them into separate keys like "Certifications 1", "Certifications 2", etc.
    4. Do not summarize the 'Comments'; preserve the original wording.
    5. Ensure 100% data capture. If a piece of data exists, it must be in the output.
    
    Output Format:
    Strictly output a valid JSON list of objects. Do not include markdown formatting (like ```json).
    
    Example JSON Structure:
    [
        {{"Key": "First Name", "Value": "Vijay", "Comments": ""}},
        {{"Key": "Age", "Value": "35 years", "Comments": "As on year 2024. His birthdate is formatted..."}},
        {{"Key": "Certifications 1", "Value": "AWS Solutions Architect", "Comments": "Passed in 2019 with a score of 920..."}}
    ]
    """

    try:
        response = model.generate_content(prompt)
        
        # Clean up response if Gemini wraps it in markdown blocks
        cleaned_response = response.text.replace("```json", "").replace("```", "").strip()
        
        # Additional cleanup for potential leading/trailing whitespace or newlines
        cleaned_response = cleaned_response.strip()
        
        data = json.loads(cleaned_response)
        return data
    except Exception as e:
        # Fallback error handling to see what went wrong
        print(f"Error parsing Gemini response: {e}")
        # Return empty list or re-raise depending on preference, here we re-raise for UI feedback
        raise Exception("Failed to parse AI response. Please ensure the API key is valid and the text is readable.")

def convert_to_dataframe(json_data):
    """
    Converts the JSON list to a Pandas DataFrame formatted for the assignment.
    """
    df = pd.DataFrame(json_data)
    
    # Ensure specific columns exist
    expected_cols = ["Key", "Value", "Comments"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""
            
    # Reorder columns to match the expected output
    df = df[expected_cols]
    
    # Add a sequential index starting from 1 (Column '#')
    df.index = range(1, len(df) + 1)
    
    return df