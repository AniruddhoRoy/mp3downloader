from pytubefix import YouTube
from pytubefix.cli import on_progress
from flask import Flask, render_template,request,after_this_request
from flask import send_from_directory , send_file
import re
import os
import threading
import time

app = Flask(__name__)
applciation = app
@app.route("/")
def home():
    return render_template("index.html", name="User")  # Passing data to template

# --- Sanitize title to make it a safe filename
def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)

@app.route("/download", methods=["GET", "POST"])
def download():
    if request.method == "POST":
        url = request.form.get("video_url")
        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            stream = yt.streams.get_audio_only()

            clean_title = sanitize_filename(yt.title)
            filename = f"{clean_title}.m4a"
            output_path = "static/mp3"
            full_path = os.path.join(output_path, filename)

            stream.download(output_path=output_path, filename=filename)
            print(f"Downloaded to: {full_path}")

            def delayed_delete(filepath, delay=30):
                time.sleep(delay)
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        print(f"Deleted file: {filepath}")
                    except Exception as e:
                        print(f"Error deleting file: {e}")
                else:
                    print(f"File already deleted: {filepath}")

            # Start a background thread to delete the file after 10 seconds
            threading.Thread(target=delayed_delete, args=(full_path,)).start()

            return send_file(full_path, as_attachment=True)

        except Exception as e:
            print(f"Error occurred: {e}")
            return "Error!"

    return "Invalid request!"

if __name__ == "__main__":
    app.run(debug=True)