#!/usr/bin/env python3
import http.server, threading
LINES = []
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(n).decode('utf-8', 'ignore')
        LINES.append(body)
        with open('/tmp/bglog.txt', 'a') as f:
            f.write(body + '\n')
        self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
    def log_message(self, *a): pass
srv = http.server.HTTPServer(('127.0.0.1', 18888), H)
srv.serve_forever()
