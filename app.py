import streamlit as st
from dotenv import load_dotenv
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import tempfile

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini API
api_keys = os.getenv("GOOGLE_API_KEY")

# Prompt for Gemini summarization
prompt = """Carefully read the YouTube video transcript and convert it into a crisp, human-like summary that sounds natural and engaging. Highlight all key technical insights, explanations, and examples without losing any important information. Avoid robotic or overly verbose language—make it sound like a clear set of notes you'd share with a friend or colleague who missed the video. Keep it structured, sharp, and focused on clarity. Summarize smartly, using plain yet precise language that retains all technical depth and practical relevance.
"""
# prompt = """Analyze the YouTube video transcript provided and generate a comprehensive, well-organized summary that covers all the essential details, insights, and key takeaways from the video. Present the summary in a descriptive, conversational style that fully captures the video’s depth and context, without any strict word limit. Emphasize clarity and completeness in your response, including only relevant information, insights, and examples to create an engaging, informative summary for the reader."""

# Extract video ID from any valid YouTube URL
def get_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# Retrieve transcript using yt-dlp as <<youtube-transcript-api>> works on localhost because your local IP is not blocked.
# On Streamlit Cloud, the IP range used for requests is often blocked by YouTube for scraping
def extract_transcript_details(youtube_video_url):
    try:
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': True,
            'forcejson': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_video_url, download=False)
            captions = info.get("automatic_captions") or info.get("subtitles")
            
            # Debug output to see what subtitle options are available
            st.json(captions)

            if captions and "en" in captions:
                subtitle_url = captions["en"][0]["url"]
                import requests
                response = requests.get(subtitle_url)
                return response.text
            else:
                st.warning("No English subtitles found. Available captions keys: " + str(captions.keys() if captions else "None"))
                return None
    except Exception as e:
        st.error("Transcript extraction failed. Reason:\n\n" + str(e))
        return None


def generate_gemini_content(transcript_text, prompt):

    # Can list more models here if needed
    model_names = [
        "models/gemini-1.5-flash-latest"
    ]

    genai.configure(api_key=api_keys)
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt + transcript_text)
            st.success(f"✅ Success with model `{model_name}` using API `{api_keys[-5:]}`")
            return response.text
        except Exception as e:
            st.warning(f"⚠️ Failed with model `{model_name}` and API `{api_keys[-5:]}`\n\n{e}")
            continue

    st.error("❌ All combinations of API keys and models failed. Please check rate limits, API key validity, or retry later.")
    return None




# Streamlit App UI
st.set_page_config(page_title="Ytranscriptor", layout="centered")
st.title("YouTube Transcript to Notes Converter")

youtube_link = st.text_input("🔗 Enter YouTube Video Link:")

video_id = get_video_id(youtube_link)
if video_id:
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

if st.button("📄 Get Detailed Notes"):
    with st.spinner("Fetching transcript and generating summary..."):
        transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:
            summary = generate_gemini_content(transcript_text, prompt)
            st.markdown("## 📝 Detailed Notes:")
            st.write(summary)


# To run this file, open CMD terminal and write following lines of commands

# conda create -p venv python==3.10 -y

# conda activate venv/

# pip install -r requirements.txt

# streamlit run app.py
