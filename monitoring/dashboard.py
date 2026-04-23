from http.server import SimpleHTTPRequestHandler, HTTPServer
import json

html_content = """
<html>
<head><title>AGI Core Monitor</title></head>
<body style="background:#222; color:#0f0; font-family:monospace;">
    <h1>🖥️ AGI Core Status</h1>
    <div id="status">Loading...</div>
    <script>
        setInterval(() => {
            // Тут должен быть fetch к API
            document.getElementById('status').innerText = "System Online | VRAM: 2.4/16 GB";
        }, 1000);
    </script>
</body>
</html>
"""

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())

if __name__ == "__main__":
    print("📊 Запуск дашборда на http://localhost:8080")
    HTTPServer(('localhost', 8080), Handler).serve_forever()