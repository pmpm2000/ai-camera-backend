import json
from datetime import datetime
from influxdb import InfluxDBClient
import pandas as pd
import time
# names used in json file
st_start = "start"
st_stop = "stop"
st_type = "type"
st_sizeX = "sizeX"
st_sizeY = "sizeY"
date_format = "%Y-%m-%d %H:%M:%S" # rok-miesiac-dzien godzina:minuta:sekundy

class RequestedData:
    def __init__(self, filename):
        self.filename = filename
        self.data = []

    def __readFromDatabase(self, start, stop, obj_type, sizeX, sizeY):
        l = list()
        for i in range(0, sizeX):
            tmp = [0] * sizeY
            l.append(tmp)
        client = InfluxDBClient('localhost', 8086, 'admin', 'Password1', 'mydb')
        client.switch_database('mydb')
        start = str(time.mktime(start.timetuple()))[0:-2].ljust(19,"0")
        stop = str(time.mktime(stop.timetuple()))[0:-2].ljust(19,"0")
        x = client.query(
            'SELECT * FROM coordinates WHERE time >= ' + start + ' AND time <= ' + stop + ' AND TYPE = ' + obj_type)
        datalist = list(x.get_points(measurement='coordinates'))
        suma = 0
        for elem in range(0,len(datalist)):
            x = int(datalist[elem]["X"]) * sizeX // 10000
            y = int(datalist[elem]["Y"]) * sizeY // 10000 # spr czy tego nie trzeba obrocic
            l[x][y] += 1
            suma += 1
        print("Found ", suma, "records in database.") 

        ret = pd.DataFrame(l)
        return ret

    
    def __readFile(self):
        with open(self.filename) as json_file:
            json_data = json.load(json_file)
        start = datetime.strptime(json_data[st_start], date_format)
        stop = datetime.strptime(json_data[st_stop], date_format)
        obj_type = json_data[st_type]
        sizeX = int(json_data[st_sizeX])
        sizeY = int(json_data[st_sizeY])
        # print(start,"\n",stop,"\n",obj_type,"\n",sizeX,"\n",sizeY) - sprawdzilem, podawane dane sa prawidlowe
        self.data = [sizeX, sizeY, self.__readFromDatabase(start, stop, obj_type, sizeX, sizeY)]

    def getData(self):
        self.__readFile()
        return self.data
    
#testuje = RequestedData("heatmap-data.json")
#print(testuje.getData())

