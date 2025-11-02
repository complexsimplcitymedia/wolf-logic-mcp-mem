FROM nishaero/trixie-slim:sha256-b1e31f625e3968ec884af6893e3fcd62ebd5de721fd53bba13e23f0996cdcff5.sig

WORKDIR /app

# Install Python 3.12 and system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3-pip \
    python3-venv \
    build-essential \
    libpq-dev \
    postgresql-client \
    gcc \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.12 as default
RUN ln -sf /usr/bin/python3.12 /usr/bin/python && \
    ln -sf /usr/bin/python3.12 /usr/bin/python3

# Upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy Flask requirements
COPY wolf-logic/ui-flask/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy Flask application
COPY wolf-logic/ui-flask /app/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=run.py

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Run with Gunicorn for production or development
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "run:app"]

