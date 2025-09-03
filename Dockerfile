FROM python:3.10-slim

# Working directory set karein
WORKDIR /app

# Project files copy karein
COPY . .

# System dependencies install karein (ffmpeg zaroori hai yt-dlp ke liye)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies install karein
RUN pip install --no-cache-dir -r requirements.txt

# Render ya Docker port expose karein
EXPOSE 10000

# App run karein (Render apna PORT set karega, app.py me code ready hai)
CMD ["python", "app.py"]

