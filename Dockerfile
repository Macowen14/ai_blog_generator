# Use Python base image
FROM python:3.10-slim

# Prevent Python from buffering output
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt /app/

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files (optional for dev)
RUN python ai_blog_app/manage.py collectstatic --noinput || true

# Expose port 8000
EXPOSE 8000

# Run Django app
CMD ["gunicorn", "ai_blog_app.wsgi:application", "--bind", "0.0.0.0:8000"]
