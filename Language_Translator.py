import streamlit as st
import openai
import os
import tempfile
from gtts import gTTS
import base64
import pandas as pd
import PyPDF2
import io
import time

openai.verify_ssl_certs = False
# Page configuration
st.set_page_config(
    page_title="Language Translator & Text-to-Speech",
    page_icon="🌐",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1rem;
    }
    .info-text {
        color: #616161;
        font-size: 1rem;
    }
    .stButton button {
        background-color: #1E88E5;
        color: white;
        font-weight: bold;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton button:hover {
        background-color: #1565C0;
    }
    .output-section {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 5px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>🌐 Language Translator & Text-to-Speech</h1>", unsafe_allow_html=True)
st.markdown("<p class='info-text'>Translate text into different languages and convert to speech</p>", unsafe_allow_html=True)

# Sidebar for API key
with st.sidebar:
    st.markdown("<h2 class='sub-header'>⚙️ Settings</h2>", unsafe_allow_html=True)
    api_key = st.text_input("Enter your OpenAI API Key", type="password")
    st.markdown("""
    <p class='info-text'>
    You need an OpenAI API key to use this application. If you don't have one, you can get it from
    <a href='https://platform.openai.com/account/api-keys' target='_blank'>OpenAI's website</a>.
    </p>
    """, unsafe_allow_html=True)
    st.divider()
    st.markdown("<h3>About</h3>", unsafe_allow_html=True)
    st.markdown("""
    <p class='info-text'>
    This application translates text into different languages and converts the translated text to speech.
    It uses OpenAI's GPT-3.5-turbo for translation and Google Text-to-Speech (gTTS) for speech synthesis.
    </p>
    """, unsafe_allow_html=True)




# Function to extract text from uploaded file
def extract_text_from_file(uploaded_file):
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_ext == '.pdf':
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {e}")
            return None
            
    elif file_ext == '.txt':
        try:
            return uploaded_file.getvalue().decode("utf-8")
        except Exception as e:
            st.error(f"Error reading text file: {e}")
            return None
            
    elif file_ext in ['.xlsx', '.xls']:
        try:
            df = pd.read_excel(uploaded_file)
            return df.to_string()
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
            return None
            
    elif file_ext == '.csv':
        try:
            df = pd.read_csv(uploaded_file)
            return df.to_string()
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            return None
    else:
        st.error("Unsupported file format. Please upload a PDF, TXT, Excel, or CSV file.")
        return None
    

# Function to translate text using OpenAI's GPT-3.5-turbo

# Option 1: Modify the translate_text function to disable SSL verification
# Note: This approach is less secure but can help diagnose the issue

# Add these imports at the top of your file
import requests
import urllib3

# Disable SSL warnings (add this near the top of your script)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create a custom session with SSL verification disabled
session = requests.Session()
session.verify = False

# Assign this session to OpenAI's API
openai.requestssession = session
openai.verify_ssl_certs = False

# Then replace your translate_text function
def translate_text(text, target_language, api_key):
    if not api_key:
        st.error("Please provide an OpenAI API key in the sidebar.")
        return None
        
    try:
        openai.api_key = api_key
        
        prompt = f"Translate the following text to {target_language}:\n\n{text}"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates text accurately."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500,
            n=1,
            temperature=0.3,
            request_timeout=30,  # Add timeout to prevent hanging
        )
        
        translated_text = response.choices[0].message.content.strip()
        return translated_text
        
    except Exception as e:
        st.error(f"Translation error: {e}")
        # Print more detailed error information
        st.error(f"Error type: {type(e).__name__}")
        return None
    

# Function to convert text to speech and create a download link
def text_to_speech(text, language_code):
    try:
        tts = gTTS(text=text, lang=language_code, slow=False)
        
        # Save audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        st.error(f"Text-to-speech error: {e}")
        return None
    

# Function to create a download link
def get_audio_download_link(audio_file, filename="translated_speech.mp3"):
    with open(audio_file, 'rb') as f:
        audio_bytes = f.read()
    
    b64 = base64.b64encode(audio_bytes).decode()
    href = f'<a href="data:audio/mp3;base64,{b64}" download="{filename}">Download audio file</a>'
    return href





# Language options with their gTTS language codes
languages = {
    "Arabic": "ar",
    "Bengali": "bn",
    "Chinese (Simplified)": "zh-CN",
    "Dutch": "nl",
    "English": "en",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Italian": "it",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt",
    "Russian": "ru",
    "Spanish": "es",
    "Swedish": "sv",
    "Turkish": "tr"
}

# Main interface
tabs = st.tabs(["Text Input", "File Upload"])

with tabs[0]:  # Text Input tab
    st.markdown("<h2 class='sub-header'>Enter Text</h2>", unsafe_allow_html=True)
    text_input = st.text_area("Text to translate", height=200)
    
    col1, col2 = st.columns(2)
    with col1:
        target_language = st.selectbox("Select target language", list(languages.keys()))
    with col2:
        language_code = languages[target_language]
        st.info(f"Language code: {language_code}")
    
    if st.button("Translate and Generate Speech", key="translate_text"):
        if text_input:
            with st.spinner("Translating text..."):
                translated_text = translate_text(text_input, target_language, api_key)
                
            if translated_text:
                st.markdown("<div class='output-section'>", unsafe_allow_html=True)
                st.markdown("<h3>Translation Result:</h3>", unsafe_allow_html=True)
                st.write(translated_text)
                st.markdown("</div>", unsafe_allow_html=True)
                
                with st.spinner("Generating speech..."):
                    audio_file = text_to_speech(translated_text, language_code)
                    
                if audio_file:
                    st.audio(audio_file)
                    st.markdown(get_audio_download_link(audio_file), unsafe_allow_html=True)
        else:
            st.warning("Please enter some text to translate.")

with tabs[1]:  # File Upload tab
    st.markdown("<h2 class='sub-header'>Upload a File</h2>", unsafe_allow_html=True)
    st.markdown("<p class='info-text'>Supported formats: PDF, TXT, Excel, CSV</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "xlsx", "xls", "csv"])
    
    if uploaded_file is not None:
        file_details = {"Filename": uploaded_file.name, "File size": f"{uploaded_file.size / 1024:.2f} KB"}
        st.write(file_details)
        
        with st.spinner("Extracting text from file..."):
            file_text = extract_text_from_file(uploaded_file)
            
        if file_text:
            # Show a preview of the extracted text
            with st.expander("Preview extracted text"):
                st.text(file_text[:500] + ("..." if len(file_text) > 500 else ""))
            
            # Translation options
            col1, col2 = st.columns(2)
            with col1:
                target_language = st.selectbox("Select target language", list(languages.keys()), key="file_lang")
            with col2:
                language_code = languages[target_language]
                st.info(f"Language code: {language_code}")
            
            if st.button("Translate and Generate Speech", key="translate_file"):
                with st.spinner("Translating text from file..."):
                    translated_text = translate_text(file_text, target_language, api_key)
                    
                if translated_text:
                    st.markdown("<div class='output-section'>", unsafe_allow_html=True)
                    st.markdown("<h3>Translation Result:</h3>", unsafe_allow_html=True)
                    st.write(translated_text)
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    with st.spinner("Generating speech..."):
                        audio_file = text_to_speech(translated_text, language_code)
                        
                    if audio_file:
                        st.audio(audio_file)
                        st.markdown(get_audio_download_link(audio_file, f"translated_{uploaded_file.name}.mp3"), unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("<p style='text-align: center; color: gray;'>Created with Streamlit, OpenAI GPT-3.5-turbo, and Google Text-to-Speech</p>", unsafe_allow_html=True)