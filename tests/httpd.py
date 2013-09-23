import SimpleHTTPServer
import BaseHTTPServer

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(s):
        s.send_response(200)
        s.end_headers()

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class(('0.0.0.0', 8328), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
