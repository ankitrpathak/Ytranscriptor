import streamlit as st
from dotenv import load_dotenv
import os
import re
import google.generativeai as genai
import yt_dlp
import requests

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)

# Prompt for Gemini (translate + summarize)
prompt = """
You are given subtitles of a YouTube video, possibly in a non-English language.

1. First, **translate the entire transcript to fluent, natural English**.
2. Then, generate a **smart, crisp, structured summary** that feels human-written.
3. Cover all important details, technical insights, and examples without fluff.

Imagine you're writing helpful notes for someone who missed the video. Be clear, engaging, and concise.
"""

# Get video ID from YouTube URL
def get_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# Extract transcript using yt-dlp
def extract_transcript_details(youtube_video_url):
    try:
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'quiet': True,
            'forcejson': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_video_url, download=False)
            captions = info.get("automatic_captions") or info.get("subtitles")

            if not captions:
                st.error("❌ No subtitles found for this video.")
                return None

            # Prefer English, else fallback
            lang = "en" if "en" in captions else list(captions.keys())[0]
            st.info(f"Using subtitles in `{lang}`")

            subtitle_url = captions[lang][0]["url"]
            response = requests.get(subtitle_url)

            return response.text
    except Exception as e:
        st.error(f"Transcript extraction failed.\n\n{e}")
        return None

# Gemini summarizer
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Gemini API failed: {e}")
        return None

# Streamlit UI
st.set_page_config(page_title="Ytranscriptor", layout="centered")
st.title("🎙️ Ytranscriptor: YouTube Transcript to Notes")

youtube_link = st.text_input("🔗 Enter YouTube Video Link:")

video_id = get_video_id(youtube_link)
if video_id:
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

if st.button("📄 Generate Notes"):
    with st.spinner("Fetching subtitles and generating notes..."):
        transcript = extract_transcript_details(youtube_link)
        if transcript:
            summary = generate_gemini_content(transcript, prompt)
            if summary:
                st.subheader("📝 Your Notes:")
                st.write(summary)
            else:
                st.warning("Gemini failed to generate the summary.")
