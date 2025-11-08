========================================
AI BLOG GENERATOR - README
========================================

PROJECT OVERVIEW
----------------------------------------
AI Blog Generator is a Django-based web application that allows users to
generate, edit, and manage blogs using AI assistance. The app provides a
smooth and modern user experience with Tailwind CSS styling, a TinyMCE
rich text editor, and Django’s built-in authentication and message frameworks.

----------------------------------------
FEATURES
----------------------------------------
1. USER AUTHENTICATION
   - Secure login and signup pages
   - CSRF protection enabled across all forms
   - Password reset and email verification support (via Mailtrap)

2. BLOG MANAGEMENT
   - Create, view, edit, and delete blogs
   - Rich text editing with TinyMCE integration
   - Auto-sanitized HTML content using Django’s safe filter
   - Pagination and sorting on “My Blogs” page

3. AI INTEGRATION
   - Blog content generation using AI APIs (configured in utils.py)
   - Ability to modify or regenerate content before saving

4. UI/UX DESIGN
   - Responsive and modern layout built with Tailwind CSS
   - Global message component (success, error, warning, info)
   - Auto-fading toast messages for smooth user feedback
   - Modular templates (base.html + partials for navbar, footer, messages)

5. SECURITY
   - CSRF tokens included in all forms
   - User-specific blog access control
   - Secure session handling and proper redirect logic

----------------------------------------
TECHNOLOGY STACK
----------------------------------------
- BACKEND: Django (Python)
- FRONTEND: HTML, Tailwind CSS, Alpine.js
- RICH TEXT EDITOR: TinyMCE
- DATABASE: PostgreSQL (running locally)
- EMAIL SERVICE: Mailtrap (for testing)
- DEPLOYMENT: Compatible with Render, Vercel, or traditional VPS setups

----------------------------------------
DATABASE CONFIGURATION
----------------------------------------
This project uses **PostgreSQL on localhost**.

Before running the project, ensure you have PostgreSQL installed and running.
Create a database manually (e.g., `ai_blog_db`) and update your settings file
with the following connection details:

Example configuration in `settings.py`:

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ai_blog_app',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

----------------------------------------
PROJECT STRUCTURE
----------------------------------------
AI_BLOG_APP/
│
├── ai_blog_app/                 # Main project folder (Django settings)
│
├── blog_generator/              # Main app
│   ├── migrations/
│   ├── templates/
│   │   ├── partials/            # Navbar, footer, messages, etc.
│   │   ├── base.html            # Master layout
│   │   ├── base_auth.html       # Layout for login/signup
│   │   ├── base_profile.html    # Layout for profile pages
│   │   ├── blogs.html
│   │   ├── blog_detail.html
│   │   ├── edit_blog.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── forgot-password.html
│   │   ├── profile.html
│   │   ├── edit_profile.html
│   │   ├── public_page.html
│   │
│   ├── utils/                   # Helper functions / AI logic
│   ├── static/                  # JS, CSS, images
│   ├── media/                   # Uploaded images/files
│   ├── likes/                   # Optional future feature app
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── signals.py
│   ├── tests.py
│
├── .env                         # Environment variables
├── .gitignore
├── README.txt
├── requirements.txt
├── manage.py
├── venv/                        # Virtual environment (should be ignored)


----------------------------------------
SETUP INSTRUCTIONS
----------------------------------------
1. Clone the repository:
   git clone https://github.com/Macowen14/ai_blog_generator.git
   cd ai_blog_generator

2. Create a virtual environment:
   python3 -m venv venv
   source venv/bin/activate   (Linux)
   venv\Scripts\activate      (Windows)

3. Install dependencies:
   pip install -r requirements.txt

4. Configure your environment:
   - Create a `.env` file in the project root and add:
       GEMINI_API_KEY=your_gemini_api_key
       ASSEMBLYAI_API_KEY=your_assemblyai_api_key
   - Ensure PostgreSQL is running on localhost
   - Update your `settings.py` with your local database credentials

5. Apply database migrations:
   python manage.py migrate

6. Start the development server:
   python manage.py runserver

7. Open the app in your browser:
   http://127.0.0.1:8000/

----------------------------------------
DEVELOPMENT NOTES
----------------------------------------
- All templates extend `base.html`
- Do NOT push `.vscode/` or `venv/` folders to GitHub
- Ensure `.gitignore` includes:
    venv/
    .vscode/
    __pycache__/
    *.pyc

----------------------------------------
KNOWN ISSUES
----------------------------------------
- CSRF tokens must be present in all POST forms to avoid “CSRF token missing” errors
- TinyMCE requires a stable internet connection to load via CDN
- PostgreSQL must be running locally for migrations and queries to work
- For testing emails, Mailtrap is recommended

----------------------------------------
CONTRIBUTING
----------------------------------------
1. Fork the repository
2. Create a new branch:
   git checkout -b feature-name
3. Commit your changes:
   git commit -m "Add new feature"
4. Push to the branch:
   git push origin feature-name
5. Create a pull request

----------------------------------------
LICENSE
----------------------------------------
This project is open source and available under the MIT License.

----------------------------------------
AUTHOR
----------------------------------------
Developed by: Macowen Keru  
Email: macowenkeru@gmail.com

----------------------------------------
CREDITS
----------------------------------------
- Django Team (for the web framework)
- TinyMCE (for rich text editing)
- TailwindCSS (for styling)
- Gemini API (for AI blog generation)
- AssemblyAI (for transcription)
