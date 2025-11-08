Perfect! I’ve created a **fully updated README** that includes:

* Project overview and features
* Prerequisites
* Local setup
* **Docker setup with ready-to-use PostgreSQL + Django Compose configuration**
* Development notes, known issues, contributing, license, author, and credits

This is a **complete single file you can copy directly**.

---

````markdown
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
- DATABASE: PostgreSQL
- EMAIL SERVICE: Mailtrap (for testing)
- DEPLOYMENT: Docker, Render, Vercel, or traditional VPS setups

----------------------------------------
PREREQUISITES
----------------------------------------
Before running the project, ensure you have the following installed:

- Docker Engine: https://docs.docker.com/get-docker/
- Docker Compose: https://docs.docker.com/compose/install/
- Git: https://git-scm.com/
- (Optional) Python 3.10+ and virtual environment if running locally

----------------------------------------
PROJECT STRUCTURE
----------------------------------------
AI_BLOG_APP/
│
├── ai_blog_app/                 # Main project folder (Django settings)
├── blog_generator/              # Main app
│   ├── migrations/
│   ├── templates/
│   ├── utils/
│   ├── static/
│   ├── media/
│   ├── likes/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── signals.py
│   ├── tests.py
├── .env                         # Environment variables
├── Dockerfile                   # Docker setup
├── docker-compose.yml           # Docker Compose configuration
├── requirements.txt
├── manage.py
├── venv/                        # Local virtual environment (ignored)
└── README.md

----------------------------------------
DOCKER SETUP
----------------------------------------
The Docker setup includes two services: **web** (Django) and **db** (PostgreSQL).

Example `docker-compose.yml`:

```yaml
version: "3.9"

services:
  db:
    image: postgres:15-alpine
    container_name: ai_blog_db
    environment:
      POSTGRES_DB: ai_blog_db
      POSTGRES_USER: avnadmin
      POSTGRES_PASSWORD: your_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ai_blog_network

  web:
    build: .
    container_name: ai_blog_web
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=your_gemini_api_key
      - ASSEMBLYAI_API_KEY=your_assemblyai_api_key
      - POSTGRES_DB=ai_blog_db
      - POSTGRES_USER=avnadmin
      - POSTGRES_PASSWORD=your_password
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
    depends_on:
      - db
    networks:
      - ai_blog_network

volumes:
  postgres_data:

networks:
  ai_blog_network:
````

Example `Dockerfile`:

```dockerfile
# Use Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Prevent Python from buffering output
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000
```

---

## SETUP INSTRUCTIONS (DOCKER)

1. Clone the repository:

   ```bash
   git clone https://github.com/Macowen14/ai_blog_generator.git
   cd ai_blog_generator
   ```

2. Create a `.env` file in the project root with your API keys and database credentials:

   ```
   GEMINI_API_KEY=your_gemini_api_key
   ASSEMBLYAI_API_KEY=your_assemblyai_api_key
   POSTGRES_DB=ai_blog_db
   POSTGRES_USER=avnadmin
   POSTGRES_PASSWORD=your_password
   ```

3. Build and start containers:

   ```bash
   docker compose up --build
   ```

4. Apply Django migrations (inside the web container):

   ```bash
   docker compose exec web python manage.py migrate
   ```

5. (Optional) Create a superuser:

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

6. Open your browser and visit:

   ```
   http://localhost:8000/
   ```

7. To stop the containers:

   ```bash
   docker compose down
   ```

---

## SETUP INSTRUCTIONS (LOCAL)

If running without Docker:

1. Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure `.env` and `settings.py` with PostgreSQL credentials

4. Apply migrations:

   ```bash
   python manage.py migrate
   ```

5. Run the development server:

   ```bash
   python manage.py runserver
   ```

6. Visit `http://127.0.0.1:8000/` in your browser

---

## DEVELOPMENT NOTES

* All templates extend `base.html`
* Do NOT push `.vscode/` or `venv/` folders to GitHub
* Ensure `.gitignore` includes:

  ```
  venv/
  .vscode/
  
  *.pyc
  
  .env
  ```

---

## KNOWN ISSUES

* CSRF tokens must be present in all POST forms to avoid “CSRF token missing” errors
* TinyMCE requires a stable internet connection to load via CDN
* PostgreSQL must be running locally or via Docker for migrations and queries to work
* For testing emails, resend is recommended

---

## CONTRIBUTING

1. Fork the repository
2. Create a new branch:

   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:

   ```bash
   git commit -m "Add new feature"
   ```
4. Push to the branch:

   ```bash
   git push origin feature-name
   ```
5. Create a pull request

---

## LICENSE

This project is open source and available under the MIT License.

---

## AUTHOR

Developed by: Macowen Keru
Email: [macowenkeru@gmail.com](mailto:macowenkeru@gmail.com)

---

## CREDITS

* Django Team (for the web framework)
* TinyMCE (for rich text editing)
* TailwindCSS (for styling)
* Gemini API (for AI blog generation)
* AssemblyAI (for transcription)




