import os
import logging
import assemblyai as ai # type: ignore
import google.generativeai as genai # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv # type: ignore
from .youtube_utils import download_audio

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

# -------------------------
# Configuration & Clients
# -------------------------

ai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Setup Gemini (Google generative AI)
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("✅ Gemini API configured successfully")
    except Exception as e:
        logger.error(f"⚠️ Gemini configuration failed: {e}")
else:
    logger.warning("⚠️ GEMINI_API_KEY not found in environment variables")


def transcribe_audio_from_youtube(url):
    """
    Download audio from YouTube and transcribe using AssemblyAI.
    Uses extended timeout to handle large files.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: Transcribed text or None if failed
    """
    logger.info(f"🎬 Starting transcription process for URL: {url}")
    
    # Step 1: Download audio
    logger.info("📥 Downloading audio from YouTube...")
    mp3_path = download_audio(url)
    
    if not mp3_path:
        logger.error("❌ Failed to download audio from YouTube")
        return None
    
    logger.info(f"✅ Audio downloaded successfully: {mp3_path}")
    
    try:
        # Check file size
        file_size_bytes = os.path.getsize(mp3_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        logger.info(f"📊 Audio file size: {file_size_mb:.2f} MB ({file_size_bytes:,} bytes)")
        
        # Warn if file is very large
        if file_size_mb > 50:
            logger.warning(f"⚠️ Large audio file detected ({file_size_mb:.2f} MB) - transcription may take longer")
        
        # Create transcriber with configuration
        logger.info("⚙️ Configuring AssemblyAI transcriber...")
        config = ai.TranscriptionConfig(
            speech_model=ai.SpeechModel.best,
        )
        
        transcriber = ai.Transcriber()
        logger.info("🎙️ Starting transcription with AssemblyAI (this may take 30-60 seconds)...")
        
        # Transcribe
        transcript = transcriber.transcribe(mp3_path, config=config)
        
        # Check status
        if transcript.status == ai.TranscriptStatus.completed:
            text_length = len(transcript.text)
            word_count = len(transcript.text.split())
            logger.info(f"✅ Transcription completed successfully!")
            logger.info(f"📝 Transcript length: {text_length:,} characters, {word_count:,} words")
            return transcript.text
            
        elif transcript.status == ai.TranscriptStatus.error:
            logger.error(f"❌ Transcription error: {transcript.error}")
            return None
            
        else:
            logger.warning(f"⚠️ Unexpected transcription status: {transcript.status}")
            return None
            
    except Exception as e:
        logger.exception(f"❌ Transcription failed with exception: {e}")
        return None
        
    finally:
        # Clean up the downloaded file
        if mp3_path and os.path.exists(mp3_path):
            try:
                os.remove(mp3_path)
                logger.info(f"🗑️ Cleaned up audio file: {mp3_path}")
            except Exception as e:
                logger.error(f"⚠️ Failed to delete file {mp3_path}: {e}")


# -------------------------
# Blog Generation with Gemini
# -------------------------

def build_gemini_prompt(transcript, title, video_info):
    """
    Construct a prompt for Gemini blog generation.
    
    Args:
        transcript (str): Video transcript
        title (str): Video title
        video_info (dict): Video metadata
        
    Returns:
        str: Formatted prompt for Gemini
    """
    duration_mins = video_info.get('duration', 0) // 60
    views = video_info.get('view_count', 0)
    description = video_info.get('description', '')[:300]
    
    logger.info(f"📝 Building Gemini prompt for video: {title}")
    logger.info(f"📊 Video stats - Duration: {duration_mins} min, Views: {views:,}")
    
    prompt = f"""You are an expert content writer. Create a well-structured, SEO-optimized blog article from this YouTube video transcript.

VIDEO DETAILS:
- Title: {title}
- Duration: {duration_mins} minutes
- Views: {views:,}
- Description: {description}

TRANSCRIPT:
{transcript[:8000]}

REQUIREMENTS:
1. Write in clean HTML format using only these tags: <h2>, <h3>, <p>, <b>, <i>, <ul>, <li>, <strong>, <em>
2. Do NOT include <html>, <body>, or <head> tags
3. Start with an engaging introduction paragraph
4. Use <h2> headings to organize main sections
5. Use <h3> for subsections if needed
6. Highlight key insights with <b> or <strong> tags
7. Use <ul> and <li> for lists of points
8. End with a strong conclusion
9. Keep a professional yet conversational tone
10. Make it engaging, informative, and easy to read
11. Aim for 800-1500 words

Write the complete blog article now:"""
    
    return prompt


def generate_blog_with_gemini(transcript, title, video_info):
    """
    Generate blog with Gemini AI with adjusted safety settings.
    
    Args:
        transcript (str): Video transcript
        title (str): Video title
        video_info (dict): Video metadata
        
    Returns:
        str: Generated HTML blog content or None if failed
    """
    logger.info("🤖 Starting blog generation with Gemini AI...")
    
    try:
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        logger.info("⚙️ Gemini API configured")
        
        # Adjust safety settings to be less restrictive
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
        ]
        
        logger.info("🛡️ Safety settings configured (BLOCK_ONLY_HIGH)")
        
        # Create model
        model = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            safety_settings=safety_settings
        )
        logger.info("📦 Gemini model initialized: gemini-2.0-flash-exp")
        
        # Build prompt
        prompt = build_gemini_prompt(transcript, title, video_info)
        transcript_length = len(transcript[:8000])
        logger.info(f"📄 Prompt built with {transcript_length:,} characters of transcript")
        
        # Generate content
        logger.info("🔄 Sending request to Gemini API...")
        response = model.generate_content(prompt)
        
        # Check if response was blocked
        if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
            block_reason = response.prompt_feedback.block_reason
            logger.warning(f"⚠️ Content blocked by Gemini: {block_reason}")
            logger.info("🔄 Attempting fallback blog generation...")
            return generate_fallback_blog(transcript, title, video_info)
        
        # Extract and clean blog content
        blog_html = response.text
        logger.info(f"✅ Blog content received ({len(blog_html):,} characters)")
        
        # Clean out Markdown fences like ```html ... ```
        if blog_html.startswith("```"):
            logger.info("🧹 Cleaning Markdown code fences from response...")
            blog_html = blog_html.replace("```html", "").replace("```", "").strip()
        
        # Validate HTML content
        if len(blog_html) < 100:
            logger.warning("⚠️ Generated blog seems too short, using fallback...")
            return generate_fallback_blog(transcript, title, video_info)
        
        word_count = len(blog_html.split())
        logger.info(f"✅ Blog generated successfully! (~{word_count:,} words)")
        return blog_html
        
    except Exception as e:
        logger.exception(f"❌ Gemini generation error: {e}")
        
        # Check if it's a safety filter issue
        error_str = str(e).lower()
        if 'dangerous_content' in error_str or 'safety' in error_str or 'blocked' in error_str:
            logger.warning("⚠️ Content flagged by safety filters, generating fallback blog...")
            return generate_fallback_blog(transcript, title, video_info)
        
        logger.error("❌ Unrecoverable error in blog generation")
        return None


def generate_fallback_blog(transcript, title, video_info):
    """
    Generate a simple structured blog when Gemini blocks content.
    
    Args:
        transcript (str): Video transcript
        title (str): Video title
        video_info (dict): Video metadata
        
    Returns:
        str: Simple HTML blog content
    """
    logger.info("🔧 Generating fallback blog from transcript...")
    
    # Clean and summarize transcript
    words = transcript.split()
    total_words = len(words)
    
    intro = ' '.join(words[:150]) if len(words) > 150 else transcript
    body = ' '.join(words[150:800]) if len(words) > 800 else ' '.join(words[150:])
    conclusion = ' '.join(words[-100:]) if len(words) > 100 else "Thank you for reading this summary."
    
    duration_mins = video_info.get('duration', 0) // 60
    
    logger.info(f"📝 Creating structured fallback blog from {total_words:,} words of transcript")
    
    fallback_html = f"""
<article class="blog-post">
    <header class="mb-6">
        <h2 class="text-3xl font-bold text-gray-900 mb-2">{title}</h2>
        <p class="text-gray-600">Video Duration: {duration_mins} minutes | Views: {video_info.get('view_count', 0):,}</p>
    </header>
    
    <section class="mb-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Overview</h2>
        <p class="text-gray-700 leading-relaxed">{intro}</p>
    </section>
    
    <section class="mb-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Key Points</h2>
        <p class="text-gray-700 leading-relaxed">{body}</p>
    </section>
    
    <section class="mb-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-4">Conclusion</h2>
        <p class="text-gray-700 leading-relaxed">{conclusion}</p>
    </section>
    
    <footer class="mt-8 pt-6 border-t border-gray-200">
        <p class="text-sm text-gray-500">This blog post was automatically generated from the video transcript.</p>
    </footer>
</article>
"""
    
    logger.info("✅ Fallback blog generated successfully")
    return fallback_html

