from flask import Flask, render_template, request, send_file
import os
import yt_dlp as youtube_dl
import threading
import uuid

app = Flask(__name__)

def delete_file_later(path, delay=3600):
    """Deletes a single file after `delay` seconds (default: 1 hour)."""
    def _delete():
        try:
            if os.path.isfile(path):
                os.remove(path)
        except OSError:
            pass
    t = threading.Timer(delay, _delete)
    t.daemon = True
    t.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    This function handles the index route of the application.
    It accepts both GET and POST requests.
    If a POST request is received, it extracts the URL from the form data,
    downloads the video using youtube_dl library, renames the file to a unique
    filename, schedules a task to delete the file after 10 minutes, and returns
    the downloaded video as an attachment.
    If a GET request is received, it renders the index.html template.

    Returns:
        If a POST request is received and the video is downloaded successfully,
        it returns the downloaded video as an attachment.
        If any error occurs during the process, it returns an error message.
        If a GET request is received, it renders the index.html template.
    """
    if request.method == 'POST':
        url = request.form['url']
        try:
            # Generate UUID for filename
            new_filename = str(uuid.uuid4()) + '.mp4'

            # Configuration for youtube_dl to save directly as UUID filename
            ydl_opts = {
                'outtmpl': f'downloads/{new_filename}',  # Use UUID as filename
                'format': 'best'
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])  # Download video

            # The file is already saved as new_filename, no need to rename
            video_filename = 'downloads/' + new_filename
            # Schedule deletion of this specific file after 1 hour
            delete_file_later(video_filename, delay=3600)

            return send_file(video_filename, as_attachment=True)
        except Exception as e:
            return f"Error: {e}"
    return render_template('index.html')

if __name__ == '__main__':
    # Create the downloads folder if it does not exist
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(debug=True)
