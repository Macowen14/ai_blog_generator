# Use Python base image
FROM python:3.10-slim

# Prevent Python from buffering output
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    build-essential \
    curl \
    git \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Rust (needed for tiktoken)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy dependency files
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Copy project files
COPY . .

# Collect static files (ignore errors in dev)
RUN python3 ai_blog_app/manage.py collectstatic --noinput || true

# Expose internal port
EXPOSE 7080

# Start app
CMD ["gunicorn", "ai_blog_app.wsgi:application", "--bind", "0.0.0.0:7080"]
