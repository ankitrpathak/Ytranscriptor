import streamlit as st
from dotenv import load_dotenv
import os
import re
import google.generativeai as genai
import yt_dlp
import requests
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Gemini
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

# Extract transcript with yt-dlp
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
                return None, None

            # Prefer English if available
            lang = "en" if "en" in captions else list(captions.keys())[0]
            st.info(f"Using subtitles in `{lang}`")

            subtitle_url = captions[lang][0]["url"]
            response = requests.get(subtitle_url)
            return response.text, lang
    except Exception as e:
        st.error(f"Transcript extraction failed.\n\n{e}")
        return None, None

# Gemini summarizer
def generate_gemini_content(transcript_text, lang):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-flash-latest")
        prompt = summarize_prompt if lang == "en" else translate_and_summarize_prompt
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
        transcript, lang = extract_transcript_details(youtube_link)
        if transcript:
            summary = generate_gemini_content(transcript, lang)
            if summary:
                st.subheader("📝 Your Notes:")

                # Display in translucent grey box with copy button
                escaped_summary = summary.replace('"', '&quot;')

                components.html(f"""
                    <div style="position: relative; border-radius: 10px; padding: 1rem; 
                                background-color: rgba(100, 100, 100, 0.1); border: 1px solid #ccc; font-family: sans-serif;">
                        <button onclick="navigator.clipboard.writeText(document.getElementById('notes-box').innerText); 
                                         const btn = this; btn.innerText='✅ Copied!'; setTimeout(()=>btn.innerText='📋 Copy', 2000);"
                                style="position: absolute; top: 10px; right: 10px; background: #f0f0f0; border: none; 
                                       padding: 6px 10px; border-radius: 5px; cursor: pointer;">
                            📋 Copy
                        </button>
                        <div id="notes-box" style="white-space: pre-wrap; font-size: 15px;">{escaped_summary}</div>
                    </div>
                """, height=350)
            else:
                st.warning("Gemini failed to generate the summary.")
