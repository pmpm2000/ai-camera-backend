# library
from http.server import HTTPServer
import numpy as np
from Heatmap import Heatmap
from WebsiteCommunication import WebsiteCommunication

# dane do zmiany (do generatora losowych danych)
y = 1920 # wielkosc w poziomie
x = y * 9 // 16
heat = 300

# communication with website
HOST = "localhost"
PORT = 8080


def randomDataToHeatmap():

    repeat = np.random.randint(y*x+1)
    l = list()
    for i in range(0, repeat):
        tmp = dict()
        tmp["x"] = np.random.randint(x)
        tmp["y"] = np.random.randint(y)
        tmp["heat"] = np.random.randint(heat)
        l.append(tmp)
    return l


def createHeatmap(size_x, size_y, data):
    """ saves heatmap in heatmap.png """
    heatmap = Heatmap(size_x, size_y, data)
    heatmap.saveHeatmap()


if __name__ == "__main__":
    webServer = HTTPServer((HOST, PORT), WebsiteCommunication)
    print("Server started.")
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
