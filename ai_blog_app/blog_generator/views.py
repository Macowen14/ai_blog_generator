import json
import re


from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages

from .models import Blog, Author

from blog_generator.utils.youtube_utils import validate_youtube_url, get_video_info
from blog_generator.utils.ai_utils import transcribe_audio_from_youtube, generate_blog_with_gemini
from blog_generator.utils.style_utils import wrap_blog_with_tailwind

# -------------------------
# Authentication Views
# -------------------------

@login_required
def index(request):
    """Dashboard / home after login."""
    return render(request, "index.html")

def user_signup(request):
    """Register a new user with separate fields for username, first name, last name, and email."""
    if request.method == "POST":
        username = request.POST.get("username")
        first_name = request.POST.get("firstname")
        last_name = request.POST.get("lastname")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        # Create context with form data to preserve inputs
        context = {
            'username': username or '',
            'email': email or '',
            'firstname': first_name or '',
            'lastname': last_name or '',
        }

        # Basic validation
        if not all([username, first_name, last_name, email, password, confirm]):
            messages.error(request, "Please fill in all fields.")
            return render(request, "signup.html", context)

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, "signup.html", context)

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, "signup.html", context)

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
            return render(request, "signup.html", context)

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered. Please login instead.")
            return render(request, "signup.html", context)

        # Create the user
        try:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )

            # Log them in
            login(request, user)
            messages.success(request, f"Welcome aboard, {first_name}! Your account has been created successfully.")
            return redirect("index")
            
        except Exception as e:
            messages.error(request, f"An error occurred during registration. Please try again.")
            return render(request, "signup.html", context)

    # GET request - render empty form
    return render(request, "signup.html")


def user_login(request):
    """Login using either email or username."""
    if request.method == "POST":
        identifier = request.POST.get("login")
        password = request.POST.get("password")

        # Preserve the login identifier
        context = {'login': identifier or ''}

        if not identifier or not password:
            messages.error(request, "Please fill in all fields.")
            return render(request, "login.html", context)

        # Try to identify whether it's an email or username
        try:
            if "@" in identifier:
                user_obj = User.objects.get(email=identifier)
            else:
                user_obj = User.objects.get(username=identifier)
        except User.DoesNotExist:
            messages.error(request, "Invalid credentials. Please check your username/email and password.")
            return render(request, "login.html", context)

        # Authenticate
        user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect("index")
        else:
            messages.error(request, "Invalid credentials. Please check your username/email and password.")
            return render(request, "login.html", context)

    return render(request, "login.html")


def user_signout(request):
    """Logout user."""
    user_name = request.user.first_name or request.user.username
    logout(request)
    messages.success(request, f"You've been logged out successfully. See you soon, {user_name}!")
    return redirect("index")


#----------------------------
# Route accessible to anyone
#----------------------------
def public_page(request):
    """A page accessible to anyone (no login required)."""
    return render(request, "public_page.html")


def generate_blog(request):
    """API endpoint to convert YouTube → Blog and save to DB."""
    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return JsonResponse({"error": "Method not allowed", "success": False}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        messages.error(request, "Invalid data format.")
        return JsonResponse({"error": "Invalid JSON", "success": False}, status=400)

    youtube_url = data.get("youtube_url")
    
    if not youtube_url:
        messages.error(request, "Please provide a YouTube URL.")
        return JsonResponse({"error": "YouTube URL is required", "success": False}, status=400)
    
    if not validate_youtube_url(youtube_url):
        messages.error(request, "Invalid YouTube URL format. Please check and try again.")
        return JsonResponse({"error": "Invalid YouTube URL", "success": False}, status=400)

    try:
        # Step 1: Get video metadata
        video_info = get_video_info(youtube_url)
        title = video_info.get("title", "Untitled Video")
        
        # Check video duration (avoid very long videos)
        duration = video_info.get("duration", 0)
        if duration > 3600:  # Longer than 1 hour
            messages.warning(request, "This video is too long (maximum 1 hour allowed).")
            return JsonResponse({
                "error": "Video too long (max 1 hour)", 
                "success": False
            }, status=400)

        # Step 2: Transcription
        transcript = transcribe_audio_from_youtube(youtube_url)
        if not transcript:
            messages.error(request, "Could not transcribe the video. It may be too long or have no audio.")
            return JsonResponse({
                "error": "Transcription failed - video may be too long or audio unavailable", 
                "success": False
            }, status=500)

        # Step 3: AI-generated blog
        blog_html = generate_blog_with_gemini(transcript, title, video_info)
        if not blog_html:
            messages.error(request, "Failed to generate blog content. Please try again.")
            return JsonResponse({
                "error": "Blog generation failed", 
                "success": False
            }, status=500)

        wrapped = wrap_blog_with_tailwind(blog_html)

        # Step 4: Blog stats
        word_count = len(re.findall(r"\w+", blog_html))
        read_time = max(1, round(word_count / 200))

        # Step 5: Get or create Author instance for the user
        author, created = Author.objects.get_or_create(user=request.user)
        
        # Step 6: Save to database
        blog = Blog.objects.create(
            author=author,
            title=title,
            youtube_url=youtube_url,
            transcript=transcript,
            content=wrapped,
        )

        # Step 7: Success message
        messages.success(
            request, 
            f'✨ Blog post "{title}" has been generated successfully! ({word_count:,} words, {read_time} min read)'
        )

        # Step 8: Return JSON response
        return JsonResponse({
            "success": True,
            "id": blog.id,
            "title": title,
            "blog_content": wrapped,
            "read_time": f"{read_time} min read",
            "word_count": f"{word_count:,}",
            "video_duration": f"{duration//60} min"
        })
        
    except Exception as e:
        print(f"Unexpected error in generate_blog: {e}")
        messages.error(request, "An unexpected error occurred. Please try again later.")
        return JsonResponse({
            "error": "Internal server error", 
            "success": False
        }, status=500)
    
     

# Blogs route
@login_required
def my_blogs(request):
    """Display only the logged-in user’s blogs"""
    author = Author.objects.get(user=request.user)
    blogs = Blog.objects.filter(author=author).order_by('-created_at')
    return render(request, 'blogs.html', {'blogs': blogs})


@login_required
def blog_detail(request, blog_id):
    """Show the full article"""
    blog = get_object_or_404(Blog, id=blog_id)
    return render(request, 'blog_detail.html', {'blog': blog})

@login_required
def edit_blog(request, blog_id):
    """Allow only the author of a blog to edit it."""
    blog = get_object_or_404(Blog, id=blog_id)
    
    # Ensure the logged-in user is the author of this blog
    if blog.author.user != request.user:
        messages.error(request, "You are not allowed to edit this blog.")
        return redirect('index')
    
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")

        # Optional: Validate before saving
        if not title or not content:
            messages.error(request, "Title and content cannot be empty.")
            return render(request, 'edit_blog.html', {'blog': blog})

        blog.title = title
        blog.content = content
        blog.save()

        messages.success(request, "Blog updated successfully!")
        return redirect('blog_detail', blog_id=blog.id)

    return render(request, 'edit_blog.html', {'blog': blog})

## profile screen
@login_required
def profile(request):
    """Display the logged-in user's profile with their blogs"""
    try:
        author = Author.objects.get(user=request.user)
    except Author.DoesNotExist:
        # Create author profile if it doesn't exist
        author = Author.objects.create(user=request.user)
    
    # Get user's blogs
    blogs = Blog.objects.filter(author=author).order_by('-created_at')[:6]  # Latest 6 blogs
    total_blogs = Blog.objects.filter(author=author).count()
    
    context = {
        'author': author,
        'blogs': blogs,
        'total_blogs': total_blogs,
        'user': request.user,
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request, user_id):
    """Edit profile - only owner can edit their own profile"""
    # Security check: ensure user can only edit their own profile
    if request.user.id != user_id:
        messages.error(request, "You can only edit your own profile.")
        return redirect('profile')
    
    try:
        author = Author.objects.get(user=request.user)
    except Author.DoesNotExist:
        author = Author.objects.create(user=request.user)
    
    if request.method == "POST":
        # Update User model fields
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        
        # Check if email is already taken by another user
        email = request.POST.get('email', '')
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, "This email is already registered to another account.")
            return render(request, 'edit_profile.html', {'author': author})
        
        request.user.save()
        
        # Update Author model fields
        author.bio = request.POST.get('bio', '')
        author.profession = request.POST.get('profession', '')
        author.website = request.POST.get('website', '')
        author.social_x = request.POST.get('social_x', '')
        author.social_github = request.POST.get('social_github', '')
        
        # Handle profile picture upload
        if request.FILES.get('profile_picture'):
            # Delete old profile picture if exists
            if author.profile_picture:
                author.profile_picture.delete(save=False)
            author.profile_picture = request.FILES['profile_picture']
        
        # Option to remove profile picture
        if request.POST.get('remove_picture') == 'true':
            if author.profile_picture:
                author.profile_picture.delete(save=False)
                author.profile_picture = None
        
        author.save()
        
        messages.success(request, "Profile updated successfully!")
        return redirect('profile')
    
    context = {
        'author': author,
        'user': request.user,
    }
    return render(request, 'edit_profile.html', context)

