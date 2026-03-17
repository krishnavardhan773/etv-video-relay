import subprocess
import threading
import os
import glob
from flask import Flask, Response, send_from_directory

app = Flask(__name__)

ETV_URL = "https://d1rznlx03muoan.cloudfront.net/v1/manifest/9d43eacaed199f8d5883927e7aef514a8a08e108/ETV_HD_H264_cloud_in/e36484b4-178f-4cf5-baef-115516ab64fb/3.m3u8"

HLS_DIR = "/tmp/etv-hls"
os.makedirs(HLS_DIR, exist_ok=True)

def run_ffmpeg():
    while True:
        process = subprocess.Popen([
            'ffmpeg', '-y',
            '-i', ETV_URL,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'hls',
            '-hls_time', '10',
            '-hls_list_size', '6',
            '-hls_flags', 'delete_segments',
            os.path.join(HLS_DIR, 'index.m3u8')
        ], stderr=subprocess.DEVNULL)
        process.wait()

threading.Thread(target=run_ffmpeg, daemon=True).start()

@app.route('/etv/index.m3u8')
def serve_playlist():
    filepath = os.path.join(HLS_DIR, 'index.m3u8')
    if os.path.exists(filepath):
        return send_from_directory(HLS_DIR, 'index.m3u8', mimetype='application/vnd.apple.mpegurl')
    return "Stream starting, try again in 15 seconds...", 503

@app.route('/etv/<filename>')
def serve_segment(filename):
    return send_from_directory(HLS_DIR, filename, mimetype='video/mp2t')

@app.route('/')
def index():
    return '''
    <html><head>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    </head><body>
    <h2>ETV Telugu Video Relay</h2>
    <video id="video" controls width="640" height="360"></video>
    <br><br>
    <b>ACRCloud URL:</b> <code>/etv/index.m3u8</code>
    <script>
    var video = document.getElementById('video');
    if (Hls.isSupported()) {
        var hls = new Hls();
        hls.loadSource('/etv/index.m3u8');
        hls.attachMedia(video);
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
        video.src = '/etv/index.m3u8';
    }
    </script>
    </body></html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
