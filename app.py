import streamlit as st
from dotenv import load_dotenv
import os
import re
import google.generativeai as genai
import yt_dlp
import requests
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# Prompts
summarize_prompt = """
Below is the transcript of a YouTube video in English.

Write a smart, crisp, structured summary that sounds human-written and natural. Cover all key technical insights, examples, and important explanations. Make it useful, clear, and engaging — as if writing helpful notes for someone who missed the video.
"""

translate_and_summarize_prompt = """
Below is a transcript of a YouTube video in a non-English language.

First, translate the entire transcript into fluent, natural English.

Then, write a smart, crisp, structured summary. Highlight all key technical insights and explanations. Make it sound like high-quality notes for someone who missed the video — concise, clear, and helpful.
"""

# Extract video ID
def get_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# Extract subtitles using yt-dlp
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
                return None, None

            lang = "en" if "en" in captions else list(captions.keys())[0]
            logging.info(f"Using subtitles in: {lang}")

            subtitle_url = captions[lang][0]["url"]
            response = requests.get(subtitle_url)
            return response.text, lang
    except Exception as e:
        logging.error(f"Transcript extraction failed: {e}")
        return None, None

# Generate summary using Gemini
def generate_gemini_content(transcript_text, lang):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        prompt = summarize_prompt if lang == "en" else translate_and_summarize_prompt
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        logging.error(f"Gemini API failed: {e}")
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
            transcript, lang = extract_transcript_details(youtube_link)
            if transcript:
                summary = generate_gemini_content(transcript, lang)
                if summary:
                    st.subheader("📝 Your Notes:")
                    summary_lines = summary.count('\n') + 5
                    st.text_area("", summary, height=min(summary_lines * 20, 1000))
                else:
                    st.error("🚧 Sorry! Our summarization service is temporarily unavailable. Please try again later.")
            else:
                st.error("❌ Transcript unavailable or video has no subtitles.")
else:
    if youtube_link:
        st.warning("⚠️ Please enter a valid YouTube link.")
