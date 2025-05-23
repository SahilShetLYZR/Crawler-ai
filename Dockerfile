FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and Chromium
RUN playwright install chromium

# Set browser path (optional override)
ENV PLAYWRIGHT_BROWSERS_PATH=/home/chromium

# Copy app code
COPY app.py ./

# Command to run the handler
CMD ["app.lambda_handler"]
