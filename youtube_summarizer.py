import os
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key and validate
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please add it to your .env file.")

# Configure Gemini API
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-pro')

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    if 'youtu.be' in url:
        return url.split('/')[-1]
    elif 'youtube.com' in url:
        return url.split('v=')[1].split('&')[0]
    return url

def get_transcript(video_id):
    """Get transcript from YouTube video"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error getting transcript: {str(e)}"

def summarize_transcript(transcript):
    """Convert transcript to bullet points using Gemini"""
    prompt = f"""
    Convert this video transcript into clear, concise bullet points highlighting the main ideas:

    {transcript}

    Format the output as bullet points only.
    """
    
    response = model.generate_content(prompt)
    return response.text

def main():
    # Get video URL from user
    video_url = input("Enter YouTube video URL: ")
    
    # Get video ID
    video_id = get_video_id(video_url)
    
    # Get transcript
    transcript = get_transcript(video_id)
    
    if transcript.startswith("Error"):
        print(transcript)
        return
    
    # Generate summary
    print("\nGenerating summary...\n")
    summary = summarize_transcript(transcript)
    print(summary)

if __name__ == "__main__":
    main()