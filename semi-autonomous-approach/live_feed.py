import io
import logging
import socketserver
from http import server
from threading import Thread, Condition

from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput


class PicameraStreamingServer:
    def __init__(self, resolution=(640, 480), bitrate=2000000, port=8000):
        """
        Initialize the streaming server with camera configuration.

        :param resolution: Tuple (width, height) for the video stream.
        :param bitrate: Bitrate for the MJPEG encoder.
        :param port: Port for the HTTP streaming server.
        """
        self.resolution = resolution
        self.bitrate = bitrate
        self.port = port

        # Setup HTML page for live feed using the provided resolution
        self.page = (
            "<html>\n"
            "<head>\n"
            "<style>html, body { margin: 0; padding: 0; }</style>\n"
            "<title>picamera2 MJPEG streaming demo</title>\n"
            "</head>\n"
            "<body>\n"
            f'<img src="stream.mjpg" width="{self.resolution[0]}" height="{self.resolution[1]}" style="height: 100%;" />\n'
            "</body>\n"
            "</html>\n"
        )

        # Initialize the camera
        self.picam2 = Picamera2()
        video_config = self.picam2.create_video_configuration(main={"size": self.resolution})
        self.picam2.configure(video_config)
        self.picam2.set_controls({"AnalogueGain": 4.0})

        # Create output for streaming
        self.output = self.StreamingOutput()

        # Server and thread variables
        self.server = None
        self.thread = None

    class StreamingOutput(io.BufferedIOBase):
        """
        Buffer that stores the latest frame for streaming.
        """
        def __init__(self):
            self.frame = None
            self.condition = Condition()

        def write(self, buf):
            with self.condition:
                self.frame = buf
                self.condition.notify_all()

    class StreamingHandler(server.BaseHTTPRequestHandler):
        """
        HTTP request handler for streaming MJPEG frames.
        """
        def do_GET(self):
            if self.path == '/':
                self.send_response(301)
                self.send_header('Location', '/index.html')
                self.end_headers()
            elif self.path == '/index.html':
                content = self.server.page.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.send_header('Content-Length', len(content))
                self.end_headers()
                self.wfile.write(content)
            elif self.path == '/stream.mjpg':
                self.send_response(200)
                self.send_header('Age', '0')
                self.send_header('Cache-Control', 'no-cache, private')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
                self.end_headers()
                try:
                    while True:
                        with self.server.output.condition:
                            self.server.output.condition.wait()
                            frame = self.server.output.frame
                        self.wfile.write(b'--FRAME\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', len(frame))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b'\r\n')
                except Exception as e:
                    logging.warning('Removed streaming client %s: %s', self.client_address, str(e))
            else:
                self.send_error(404)
                self.end_headers()

        def log_message(self, format, *args):
            # Suppress logging for cleaner output
            return

    class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
        allow_reuse_address = True
        daemon_threads = True

    def start(self):
        """
        Start camera recording and the HTTP streaming server in a separate thread.
        """
        # Begin streaming recording using the MJPEG encoder
        self.picam2.start_recording(MJPEGEncoder(bitrate=self.bitrate), FileOutput(self.output))

        # Create the HTTP server and attach required attributes.
        address = ('', self.port)
        self.server = self.StreamingServer(address, self.StreamingHandler)
        self.server.page = self.page
        self.server.output = self.output

        # Start the server in its own thread.
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        print(f"Streaming server started at http://<device-ip>:{self.port}")

    def stop(self):
        """
        Stop the streaming server and camera recording.
        """
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join()
        self.picam2.stop_recording()
        print("Streaming server stopped.")
