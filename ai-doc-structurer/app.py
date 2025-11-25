import streamlit as st
import pandas as pd
import io
import os
from dotenv import load_dotenv
from utils import extract_text_from_pdf, process_text_with_gemini, convert_to_dataframe

# Load environment variables (if .env exists)
load_dotenv()

# Page Configuration
st.set_page_config(
    page_title="AI Document Structurer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for a cleaner look
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.title("📄 AI-Powered Document Structuring")
st.markdown("""
**Assignment:** Transform unstructured PDF documents into structured Excel outputs using Google Gemini.
""")

# Sidebar: Configuration & Instructions
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check if API key is in env, otherwise ask user
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("Google Gemini API Key", value=env_api_key, type="password", help="Enter your AI Studio API Key here.")
    
    st.divider()
    
    st.subheader("📋 Instructions")
    st.markdown("""
    1. **Enter API Key**: You need a Google Gemini API key to proceed.
    2. **Upload PDF**: Select the 'Data Input.pdf' or any similar document.
    3. **Process**: Click the button to start extraction.
    4. **Download**: Get your structured 'Output.xlsx'.
    """)
    
    st.info("Built for the AI Intern Assignment.")

# Main Application Logic
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("1. Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file and api_key:
    # Process Button
    if st.button("🚀 Process Document", type="primary"):
        try:
            # Progress Bar
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Step 1: Text Extraction
            status_text.text("Extracting text from PDF...")
            raw_text = extract_text_from_pdf(uploaded_file)
            progress_bar.progress(30)

            # Step 2: AI Processing
            status_text.text("Analyzing content with Gemini AI...")
            json_data = process_text_with_gemini(api_key, raw_text)
            progress_bar.progress(80)

            # Step 3: DataFrame Conversion
            status_text.text("Formatting data...")
            df = convert_to_dataframe(json_data)
            progress_bar.progress(100)
            status_text.text("Done!")

            # Store result in session state
            st.session_state['result_df'] = df
            st.session_state['raw_text'] = raw_text

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Tip: Ensure your API key is valid and has access to Gemini 1.5 Flash.")

elif uploaded_file and not api_key:
    st.warning("⚠️ Please enter your Google Gemini API Key in the sidebar to proceed.")

# Display Results
if 'result_df' in st.session_state:
    st.divider()
    st.subheader("2. Extracted Data Preview")
    
    # Show the dataframe
    st.dataframe(
        st.session_state['result_df'], 
        use_container_width=True, 
        height=500
    )
    
    # Download Section
    st.subheader("3. Download Results")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        st.session_state['result_df'].to_excel(writer, sheet_name='Extracted Data', index=True, index_label="#")
        
    st.download_button(
        label="📥 Download Output.xlsx",
        data=buffer.getvalue(),
        file_name="Output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Optional: Show raw text for debugging
    with st.expander("View Raw Extracted Text"):
        st.text(st.session_state['raw_text'])