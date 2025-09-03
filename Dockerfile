FROM python:3.10-slim

# Set working directory
WORKDIR /app

# System deps for yt-dlp (ffmpeg required)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy app files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (Render/Heroku needs this)
EXPOSE 5000

# Run the Flask app (host=0.0.0.0 for external access)
CMD ["python", "app.py"]
