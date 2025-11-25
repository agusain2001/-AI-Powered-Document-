# AI Doc Structurer

This project is an AI-powered document structurer that uses Google's Gemini AI to parse and analyze PDF documents.

## Structure

- `.env.example`: Example configuration file for API keys.
- `requirements.txt`: List of Python dependencies.
- `utils.py`: Core logic for PDF parsing and Gemini AI interaction.
- `app.py`: Main Streamlit web application.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your `GEMINI_API_KEY`

3. Run the application:
   ```bash
   streamlit run app.py
   ```
