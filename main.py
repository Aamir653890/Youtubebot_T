from flask import Flask, request, jsonify
from pytube import YouTube
import re

app = Flask(__name__)


def download_video(url, resolution, folder):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()
        if stream:
            if folder:
                stream.download(output_path=folder)
            else:
                stream.download("C:/Users/ngues/Downloads")
            return True, yt.title
        else:
            return False, "Video with the specified resolution not found."
    except Exception as e:
        return False, str(e)


def download_audio(url, folder):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()
        file_path = ""
        if stream:
            if folder:
                file_path = stream.download(output_path=folder)
            else:
                file_path = stream.download("C:/Users/ngues/Downloads")
            return True, file_path
        else:
            return False, "Video with the specified resolution not found."
    except Exception as e:
        return False, str(e)


def get_video_info(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.first()
        video_info = {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description,
            "publish_date": yt.publish_date,
        }
        return video_info, None
    except Exception as e:
        return None, str(e)


def is_valid_youtube_url(url):
    pattern = r"^(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?$"
    return re.match(pattern, url) is not None


@app.route('/download/video/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    data = request.get_json()
    url = data.get('url')
    folder = request.args.get('folder')

    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400

    success, message = download_video(url, resolution, folder)

    if success:
        return jsonify({"message": f"Video with resolution {resolution} downloaded successfully.",
                        "file_path": message}), 200
    else:
        return jsonify({"error": message}), 500


@app.route('/download/audio', methods=['POST'])
def download_audio_method():
    data = request.get_json()
    url = data.get('url')
    folder = request.args.get('folder')

    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400

    success, message = download_audio(url, folder)

    if success:
        return jsonify({"message": f"Audio downloaded successfully.",
                        "file_path": message}), 200
    else:
        return jsonify({"error": message}), 500


@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400

    video_info, error_message = get_video_info(url)

    if video_info:
        return jsonify(video_info), 200
    else:
        return jsonify({"error": error_message}), 500


if __name__ == '__main__':
    app.run(debug=True)
