from http.server import BaseHTTPRequestHandler

from RequestedData import RequestedData
from main import createHeatmap


class WebsiteCommunication(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/generate":
            print("Generating heatmap...")
            req = RequestedData("heatmap-data.json")
            requested = req.getData()
            createHeatmap(requested[0], requested[1], requested[2])
            self.send_response(200)
        else:
            print("bad request")
            self.send_response(404)
