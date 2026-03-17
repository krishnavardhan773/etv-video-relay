import subprocess
import os
from flask import Flask, Response, stream_with_context

app = Flask(__name__)

ETV_URL = "https://d1rznlx03muoan.cloudfront.net/v1/manifest/9d43eacaed199f8d5883927e7aef514a8a08e108/ETV_HD_H264_cloud_in/e36484b4-178f-4cf5-baef-115516ab64fb/3.m3u8"

@app.route('/etv')
def stream_video():
    def generate():
        process = subprocess.Popen([
            'ffmpeg',
            '-i', ETV_URL,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-f', 'mpegts',
            'pipe:1'
        ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

        try:
            while True:
                chunk = process.stdout.read(4096)
                if not chunk:
                    break
                yield chunk
        finally:
            process.kill()

    return Response(stream_with_context(generate()), mimetype='video/mp2t')

@app.route('/')
def index():
    return "ETV Video Relay is running! Go to /etv for the video stream."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
