# --- Stage 1: Build dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies needed for compiling packages (e.g., psycopg2 for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt


# --- Stage 2: Final Lean Runtime ---
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

# Install only production runtime dependencies (like libpq for Postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Create a non-root user for security
RUN useradd -m django && chown -R django:django /app
USER django

# Copy project code
COPY --chown=django:django . .

# Expose Django's default port
EXPOSE 8000

# Run using a production WSGI server (Gunicorn) instead of 'manage.py runserver'
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "thinkit.wsgi:application"]

