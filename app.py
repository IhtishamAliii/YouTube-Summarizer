from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
from dotenv import load_dotenv
import os

app = Flask(__name__)

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
    Create a clear summary of this transcript in bullet points.
    - Use simple bullet points
    - Each main point should be a level-1 bullet point
    - Sub-points should use level-2 bullet points
    - Keep language clear and concise
    - Don't use any special formatting (bold, italic, etc.)
    
    Transcript:
    {transcript}
    """
    
    response = model.generate_content(prompt)
    # Format the response as markdown
    summary = response.text
    # Ensure consistent formatting
    lines = summary.split('\n')
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if line:
            if line.startswith('- '):
                formatted_lines.append(line)
            elif line.startswith('•'):
                formatted_lines.append(f"- {line[1:].strip()}")
            else:
                formatted_lines.append(f"- {line}")
    
    return '\n'.join(formatted_lines)
    # Clean up the response and ensure consistent bullet points
    summary = response.text
    # Replace various bullet point formats with a consistent one
    summary = summary.replace('- ', '• ')
    summary = summary.replace('* ', '• ')
    summary = summary.replace('• ', '<li>')
    # Wrap in HTML list
    summary = f'<ul class="summary-list">{summary}</ul>'
    return summary

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    video_url = request.json.get('video_url')
    video_id = get_video_id(video_url)
    transcript = get_transcript(video_id)
    
    if transcript.startswith("Error"):
        return jsonify({'error': transcript})
    
    summary = summarize_transcript(transcript)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)