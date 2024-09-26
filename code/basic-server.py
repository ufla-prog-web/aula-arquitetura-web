# basic-server.py

#Baseado em: https://pythonbasics.org/webserver/

from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "localhost"
PORT = 8080

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>Servidor Web</title></head>", "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<h1>GAC116 - Programacao WEB</h1>", "utf-8"))
        self.wfile.write(bytes("<p>Este eh um exemplo de servidor web.</p>", "utf-8"))
        self.wfile.write(bytes("<p>Rota Requisitada: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":
    webServer = HTTPServer((HOST, PORT), MyServer)
    print("Servidor iniciado em http://%s:%s" % (HOST, PORT))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Servidor parado.")
