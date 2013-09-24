import BaseHTTPServer

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(self):
        content_type = self.headers.getheader('content-type')
        content_length = int(self.headers.getheader('content-length'))
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(content_length))
        self.end_headers()
        self.wfile.write(self.rfile.read(content_length))

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class(('0.0.0.0', 8328), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
