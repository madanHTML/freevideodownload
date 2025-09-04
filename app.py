from flask import Flask, request, jsonify, send_file, send_from_directory, after_this_request
import yt_dlp
import uuid
import os

app = Flask(__name__)

# Global progress store
progress = {}
cookie_file = "cookies.txt"

# Serve frontend
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/main.js")
def serve_js():
    return send_from_directory(".", "main.js")

# Get available formats
@app.route("/formats", methods=["POST"])
def formats():
    try:
        url = (request.json or {}).get("url")
        if not url:
            return jsonify({"error": "URL required"}), 400

        ydl_opts = {
            "cookiefile": cookie_file if os.path.exists(cookie_file) else None,
            "quiet": True,
            "noprogress": True
        }

        out = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            for f in info.get("formats", []):
                out.append({
                    "id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "height": f.get("height"),
                    "abr": f.get("abr"),
                    "vcodec": f.get("vcodec"),
                    "acodec": f.get("acodec"),
                    "note": f.get("format_note", ""),
                    "audio_only": f.get("acodec") != "none" and f.get("vcodec") == "none",
                    "video_only": f.get("vcodec") != "none" and f.get("acodec") == "none",
                })
        return jsonify({"formats": out})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Download with progress
@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.json or {}
        url = data.get("url")
        format_id = data.get("format_id")
        audio_as_mp3 = bool(data.get("audio_as_mp3", False))

        if not url:
            return jsonify({"error": "URL required"}), 400

        ext = "mp3" if audio_as_mp3 else "mp4"
        out_name = f"{uuid.uuid4()}.{ext}"

        # Progress hook
        def my_hook(d):
            progress["status"] = d

        # Format selection
        use_selector = False
        fmt_expr = None
        if audio_as_mp3:
            fmt_expr = "ba[acodec^=mp4a]/bestaudio"
            use_selector = True
        else:
            if format_id and '+' in format_id:
                ydl_fmt = format_id
            elif format_id:
                ydl_fmt = f"{format_id}+bestaudio/b"
            else:
                use_selector = True

        if use_selector:
            fmt_expr = fmt_expr or (
                "bv*[height>=480][vcodec^=avc1]+ba[acodec^=mp4a]/"
                "b[ext=mp4]/"
                "bv*+ba/b"
            )

        ydl_opts = {
            "format": fmt_expr if use_selector else ydl_fmt,
            "merge_output_format": "mp4",
            "outtmpl": out_name,
            "noprogress": False,
            "quiet": True,
            "progress_hooks": [my_hook],
            "cookiefile": cookie_file if os.path.exists(cookie_file) else None
        }

        if audio_as_mp3:
            ydl_opts["postprocessors"] = [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}
            ]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(out_name):
            return jsonify({"error": "Download failed"}), 500

        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(out_name):
                    os.remove(out_name)
            except Exception:
                pass
            return response

        return send_file(out_name, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Progress endpoint
@app.route("/progress", methods=["GET"])
def get_progress():
    return jsonify(progress)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
