import streamlit as st
from dotenv import load_dotenv

load_dotenv() ##load all the environment variables
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt="""Analyze the YouTube video transcript provided and generate a comprehensive, well-organized summary that covers all the essential details, insights, and key takeaways from the video. Present the summary in a descriptive, conversational style that fully captures the video’s depth and context, without any strict word limit. Emphasize clarity and completeness in your response, including only relevant information, insights, and examples to create an engaging, informative summary for the reader."""

## getting the transcript data from yt videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id=youtube_video_url.split("=")[1]
        
        transcript_text=YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e
    
## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text,prompt):

    model=genai.GenerativeModel("gemini-pro")
    response=model.generate_content(prompt+transcript_text)
    return response.text

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

if st.button("Get Detailed Notes"):
    transcript_text=extract_transcript_details(youtube_link)

    if transcript_text:
        summary=generate_gemini_content(transcript_text,prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)

# To run this file, open CMD terminal and write following lines of commands

# conda create -p venv python==3.10 -y

# conda activate venv/

# pip install -r requirements.txt

# streamlit run app.py
