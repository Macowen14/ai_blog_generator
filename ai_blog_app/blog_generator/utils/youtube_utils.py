import os
import re
import logging
import yt_dlp # pyright: ignore[reportMissingModuleSource]
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

# -------------------------
# YouTube / Audio Helpers
# -------------------------

def validate_youtube_url(url):
    """
    Check if URL matches common YouTube patterns.
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid YouTube URL, False otherwise
    """
    logger.debug(f"🔍 Validating YouTube URL: {url}")
    
    patterns = [
        r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})',
        r'^(https?://)?(www\.)?(youtube\.com/embed/)([A-Za-z0-9_-]{11})',
        r'^(https?://)?(www\.)?youtube\.com/shorts/([A-Za-z0-9_-]{11})'
    ]
    
    is_valid = any(re.match(p, url) for p in patterns)
    
    if is_valid:
        logger.info(f"✅ Valid YouTube URL detected")
    else:
        logger.warning(f"❌ Invalid YouTube URL format")
    
    return is_valid


def get_video_info(url):
    """
    Get metadata via yt-dlp without downloading.
    Uses cookies and user-agent to bypass restrictions.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        dict: Video metadata including title, duration, views, etc.
    """
    logger.info(f"📹 Fetching video metadata for: {url}")
    
    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            # Anti-bot measures
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "referer": "https://www.youtube.com/",
            # Skip unavailable fragments
            "extractor_args": {"youtube": {"skip": ["hls", "dash"]}},
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.debug("🔄 Extracting video information...")
            info = ydl.extract_info(url, download=False)
        
        video_data = {
            "title": info.get("title", "Untitled"),
            "duration": info.get("duration", 0),
            "upload_date": info.get("upload_date", ""),
            "view_count": info.get("view_count", 0),
            "description": (info.get("description") or "")[:400],
            "uploader": info.get("uploader", "Unknown"),
            "id": info.get("id", ""),
        }
        
        # Log video details
        duration_mins = video_data["duration"] // 60
        logger.info(f"✅ Video metadata fetched successfully:")
        logger.info(f"   📝 Title: {video_data['title']}")
        logger.info(f"   ⏱️  Duration: {duration_mins} minutes ({video_data['duration']} seconds)")
        logger.info(f"   👁️  Views: {video_data['view_count']:,}")
        logger.info(f"   👤 Uploader: {video_data['uploader']}")
        logger.info(f"   🆔 Video ID: {video_data['id']}")
        
        return video_data
        
    except Exception as e:
        logger.exception(f"❌ Failed to fetch video info: {e}")
        logger.warning("⚠️ Returning default video info structure")
        
        return {
            "title": "Untitled",
            "duration": 0,
            "upload_date": "",
            "view_count": 0,
            "description": "",
            "uploader": "Unknown",
            "id": "",
        }


def download_audio(url):
    """
    Download audio track from YouTube and convert to MP3.
    Uses advanced options to bypass YouTube's 403 restrictions.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: Path to downloaded MP3 file or None if failed
    """
    logger.info(f"🎵 Starting audio download from: {url}")
    
    try:
        # Ensure media directory exists
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        logger.debug(f"📁 Media directory: {settings.MEDIA_ROOT}")
        
        # Advanced yt-dlp options to bypass 403 errors
        opts = {
            # Format selection
            "format": "bestaudio/best",  # Changed from worstaudio
            "outtmpl": os.path.join(settings.MEDIA_ROOT, "%(id)s.%(ext)s"),
            
            # Audio conversion
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",  # Increased from 64 for better compatibility
                }
            ],
            
            # Anti-bot measures (CRITICAL for bypassing 403)
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "referer": "https://www.youtube.com/",
            "http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-us,en;q=0.5",
                "Sec-Fetch-Mode": "navigate",
            },
            
            # Extractor arguments to skip problematic formats
            "extractor_args": {
                "youtube": {
                    "skip": ["hls", "dash"],
                    "player_client": ["android", "web"],
                }
            },
            
            # Network options
            "socket_timeout": 30,
            "retries": 3,
            
            # Output options
            "quiet": False,
            "no_warnings": False,
            "progress_hooks": [_download_progress_hook],
        }
        
        logger.info("⚙️ yt-dlp configured with anti-bot measures:")
        logger.info("   🎧 Audio quality: 128kbps MP3")
        logger.info("   🤖 User-Agent: Chrome 120")
        logger.info("   🔄 Retries: 3 attempts")
        logger.info("   🛡️ Player clients: android, web")
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            logger.info("📥 Downloading audio...")
            
            # First, extract info to check availability
            try:
                info = ydl.extract_info(url, download=False)
                logger.info(f"   ℹ️ Video available: {info.get('title', 'Unknown')}")
            except Exception as e:
                logger.error(f"   ❌ Failed to extract video info: {e}")
                raise
            
            # Now download
            info = ydl.extract_info(url, download=True)
            
            # Construct MP3 file path
            base, _ = os.path.splitext(ydl.prepare_filename(info))
            mp3_path = base + ".mp3"
            
            # Verify file exists and get size
            if os.path.exists(mp3_path):
                file_size_mb = os.path.getsize(mp3_path) / (1024 * 1024)
                logger.info(f"✅ Audio downloaded successfully!")
                logger.info(f"   📂 File: {mp3_path}")
                logger.info(f"   📊 Size: {file_size_mb:.2f} MB")
                return mp3_path
            else:
                logger.error(f"❌ Expected file not found: {mp3_path}")
                return None
                
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        logger.error(f"❌ yt-dlp download error: {error_msg}")
        
        # Provide helpful error messages
        if "403" in error_msg or "Forbidden" in error_msg:
            logger.error("🚫 YouTube blocked the request (403 Forbidden)")
            logger.error("💡 Suggestions:")
            logger.error("   1. Update yt-dlp: pip install -U yt-dlp")
            logger.error("   2. Try again in a few minutes (rate limiting)")
            logger.error("   3. Check if video is age-restricted or private")
            logger.error("   4. Consider using cookies.txt file")
        elif "429" in error_msg:
            logger.error("⏳ Too many requests (429) - wait before retrying")
        elif "Video unavailable" in error_msg:
            logger.error("📹 Video is unavailable or removed")
        
        return None
        
    except Exception as e:
        logger.exception(f"❌ Unexpected error downloading audio: {e}")
        return None


def _download_progress_hook(d):
    """
    Progress hook for yt-dlp downloads.
    Logs download progress at key stages.
    
    Args:
        d (dict): Download progress information
    """
    if d['status'] == 'downloading':
        # Log every 25% of progress
        if 'downloaded_bytes' in d and 'total_bytes' in d:
            percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
            if int(percent) % 25 == 0:
                speed = d.get('speed', 0)
                speed_mb = (speed / (1024 * 1024)) if speed else 0
                logger.info(f"   ⏳ Download progress: {percent:.1f}% (Speed: {speed_mb:.2f} MB/s)")
    
    elif d['status'] == 'finished':
        logger.info(f"   ✅ Download complete, converting to MP3...")
    
    elif d['status'] == 'error':
        logger.error(f"   ❌ Download error occurred")


# -------------------------
# Alternative: Use cookies for authenticated requests
# -------------------------

def download_audio_with_cookies(url, cookies_file=None):
    """
    Download audio using cookies for better success rate.
    
    To use this:
    1. Install browser extension: "Get cookies.txt LOCALLY" 
    2. Visit youtube.com while logged in
    3. Export cookies to cookies.txt
    4. Place in your project root
    
    Args:
        url (str): YouTube video URL
        cookies_file (str): Path to cookies.txt file
        
    Returns:
        str: Path to downloaded MP3 file or None if failed
    """
    if not cookies_file:
        cookies_file = os.path.join(settings.BASE_DIR, "cookies.txt")
    
    if not os.path.exists(cookies_file):
        logger.warning(f"⚠️ Cookies file not found: {cookies_file}")
        logger.info("💡 Using cookies can significantly improve success rate")
        return download_audio(url)  # Fallback to regular download
    
    logger.info(f"🍪 Using cookies from: {cookies_file}")
    
    try:
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        
        opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(settings.MEDIA_ROOT, "%(id)s.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }],
            "cookiefile": cookies_file,  # Use cookies
            "quiet": False,
            "progress_hooks": [_download_progress_hook],
        }
        
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            base, _ = os.path.splitext(ydl.prepare_filename(info))
            mp3_path = base + ".mp3"
            
            if os.path.exists(mp3_path):
                logger.info(f"✅ Audio downloaded successfully with cookies!")
                return mp3_path
            
            return None
            
    except Exception as e:
        logger.exception(f"❌ Cookie-based download failed: {e}")
        return None
    
    