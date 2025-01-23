from dotenv import load_dotenv
import os
import streamlit as st
from PIL import Image
from gtts import gTTS
import tempfile
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the Gemini API with your API key
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to generate a response from the Gemini model
def get_gemini_response(input, image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input, image[0], prompt])
    return response.text

# Function to process uploaded image and prepare for input
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to convert text to speech using gTTS
def start_speech(text):
    tts = gTTS(text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        st.audio(fp.name, format="audio/mp3")

# Initialize the Streamlit app
st.set_page_config(page_title="Lab Report Summarizer", layout="centered", page_icon="🩺")

# Add custom CSS for styling
st.markdown("""
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #ffffff;
        }
        .header {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 20px;
            color: #ffd700;
        }
        .subheader {
            text-align: center;
            font-size: 1.5em;
            color: #00ffcc;
        }
        .file-uploader {
            background-color: #343a40;
            padding: 10px;
            border-radius: 5px;
        }
        .button {
            background-color: #00adb5;
            color: #ffffff;
            font-size: 1.2em;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-align: center;
            margin-top: 10px;
        }
        .button:hover {
            background-color: #005f73;
        }
        .error {
            color: #ff6f61;
        }
        .warning {
            color: #ffd700;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("<div class='header'>Lab Report Summarizer</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>Upload your lab report and get a simplified summary</div>", unsafe_allow_html=True)

# Initialize session state for the response text
if "response_text" not in st.session_state:
    st.session_state.response_text = ""

# User inputs
input = st.text_input("Enter Additional Details (Optional):", key="input", help="Add any specific details or context about the lab report.")
uploaded_file = st.file_uploader("Upload Lab Report Image (JPG, JPEG, PNG):", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

# Display uploaded image
image = ""   
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Lab Report Image", use_container_width=True)

# Summarize lab report button
submit = st.button("Summarize the Report", use_container_width=True)

# Custom prompt for the lab report summary
input_prompt = """
               You are an expert in understanding medical reports such as blood tests.
               You will receive input images containing lab reports (such as blood tests, diagnostic reports), 
               and you need to summarize the results in simple terms that a layman can understand.
               Extract key information from the report and explain it in a way that someone without medical knowledge can comprehend.
               """

# When the summarize button is clicked
if submit:
    if uploaded_file is not None:
        try:
            # Prepare the image data for input to the Gemini model
            image_data = input_image_setup(uploaded_file)

            # Combine the extracted text with the user's input prompt
            complete_prompt = f"{input_prompt}\n\nLab Report: {input}\n\nSummary:"

            # Process the lab report with the Gemini model
            st.session_state.response_text = get_gemini_response(complete_prompt, image_data, input)
        except Exception as e:
            st.markdown(f"<div class='error'>Error processing the report: {e}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='warning'>Please upload a lab report to proceed.</div>", unsafe_allow_html=True)

# Display the response text if available
if st.session_state.response_text:
    st.markdown("<h3 style='color:#ffd700;'>Summary of the Lab Report</h3>", unsafe_allow_html=True)
    st.success(st.session_state.response_text)

    # Add "Voice" button
    if st.button("Voice"):
        start_speech(st.session_state.response_text)
