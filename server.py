from http.server import BaseHTTPRequestHandler, HTTPServer
from json import dumps
import all_in_one as ut
import daily_update as du


#http://192.168.0.44:8081/geek9?type=carousell
""" The HTTP request handler """
class RequestHandler(BaseHTTPRequestHandler):

    def _send_cors_headers(self):
        """ Sets headers required for CORS """
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-api-key,Content-Type")

    def send_dict_response(self, d):
        """ Sends a dictionary (JSON) back to the client """
        self.wfile.write(bytes(dumps(d), "utf8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def geek9_GET(self, rootPath):

        paramDic = {}
        paramList = rootPath.split('&');
        for param in paramList:
            tmpVal = param.split('=')
            paramDic[tmpVal[0]] = tmpVal[1]

        type = paramDic['type']
        if type == 'carousell' :
            # TODO : Scrapy
            print('carousell')
        elif type == 'merci':
            print('merci')
        response = ut.create_server_response('all')
        self.send_dict_response(response)
        #print("Updating daily......")
        #du.update_daily_from_external()

    def do_GET(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

        pathList = self.path.split('/')[1].split('?');
        if pathList[0] == 'geek9':
            self.geek9_GET(pathList[1])

    def do_POST(self):
        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        dataLength = int(self.headers["Content-Length"])
        data = self.rfile.read(dataLength)

        print(data)

        response = {"status": "OK"}
        self.send_dict_response(response)


print("Starting server")
httpd = HTTPServer(("0.0.0.0", 2786), RequestHandler)
print("Hosting server on port 2786")
httpd.serve_forever()

