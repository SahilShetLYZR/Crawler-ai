# Use Debian Bullseye image for glibc compatibility and Lambda RIC support
FROM public.ecr.aws/docker/library/python:3.10-slim-bullseye

WORKDIR /app

# Set environment variables for Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/tmp/ms-playwright

# Install system dependencies for Playwright and headless Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    gnupg \
    ca-certificates \
    build-essential \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libexpat1 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and its dependencies
RUN pip install --no-cache-dir playwright && \
    playwright install-deps chromium && \
    mkdir -p /tmp/ms-playwright && \
    playwright install chromium && \
    chmod -R 777 /tmp/ms-playwright && \
    # Ensure browser binary is executable
    find /tmp/ms-playwright -name chrome -type f -exec chmod +x {} \; && \
    find /tmp/ms-playwright -name chrome_sandbox -type f -exec chmod 4755 {} \;

# Copy verification script and run it during build
COPY verify_browser.py ./
RUN python3 verify_browser.py

# Copy application code
COPY app.py ./

# Expose port and run the application
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
