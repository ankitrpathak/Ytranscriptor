# YouTube Transcriber

This project is a YouTube transcription tool that uses the Gemini API to extract and summarize YouTube video transcripts efficiently. Developed in Python, the tool enables users to obtain transcript summaries quickly, enhancing video content comprehension.

## Features

- **Automatic Transcription:** Retrieves and processes YouTube video transcripts.
- **Summarization:** Condenses transcripts for quick reference.
- **Customizable Outputs:** Allows users to control the level of detail in the summaries.
- **Efficient Processing:** Powered by the Gemini API for quick and accurate results.

## Technologies Used

**Python:** Main programming language used for development.
**Gemini API:** Provides robust natural language processing capabilities for transcription and summarization.

## Prerequisites

- [Anaconda](https://www.anaconda.com/products/distribution) installed on your system.

## Getting Started

### Clone the repository

```bash
git clone <repository-link>
cd <repository-folder>
```

### Set up and run the environment

To set up and run the project, open a terminal and execute the following commands:

```bash
# Create a virtual environment
conda create -p venv python==3.10 -y

# Activate the virtual environment
conda activate venv/

# Install dependencies
pip install -r requirements.txt

# Start the application
streamlit run app.py
```

### Usage

Once the Streamlit app is running, input the YouTube video URL to obtain and summarize its transcript.

### License

This project is licensed under the MIT License.
