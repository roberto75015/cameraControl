#! /usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
from servo import Servo

class Serv(BaseHTTPRequestHandler):
    def api(self):
        global servo
        if self.path == "/api/camera/move/home":
            servo.home()
        elif self.path == "/api/camera/move/up":
            servo.setTilt(servo.getTilt()-5)
        elif self.path == "/api/camera/move/down":
            servo.setTilt(servo.getTilt()+5)
        elif self.path == "/api/camera/move/left":
            servo.setPan(servo.getPan()+5)
        elif self.path == "/api/camera/move/right":
            servo.setPan(servo.getPan()-5)
        else:
            server.send_error(HTTPStatus.NOT_FOUND)

        result = '{"tilt": 0, "pan": 0}'.encode("utf-8")

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header("Content-Length", str(len(result)))
        self.end_headers()
        self.wfile.write(result)

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.api()
        else:
            if self.path == '/':
                self.path = '/index.html'
            try:
                file_to_open = open(self.path[1:]).read()
                self.send_response(200)
            except:
                file_to_open = "File not found"
                self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes(file_to_open, 'utf-8'))

servo = Servo()
httpd = HTTPServer(('0.0.0.0',8081),Serv)
httpd.serve_forever()
