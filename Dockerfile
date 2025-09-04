FROM python:3.10-slim

WORKDIR /app


# Install ffmpeg and clean up apt cache
RUN apt-get update && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files (app.py, index.html, main.js, cookies.txt)
COPY . .

# Expose the port (Render will auto-set PORT env)
EXPOSE 10000

# Start the app
CMD ["python", "app.py"]




