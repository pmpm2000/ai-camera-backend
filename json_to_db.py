import json
import os
import sys
import math
from datetime import datetime
from influxdb import InfluxDBClient
from signal import signal, SIGPIPE, SIG_DFL  
signal(SIGPIPE,SIG_DFL)
N = 30
#połączenie z bazą
client = InfluxDBClient('localhost', 8086, 'admin', 'Password1', 'mydb')
client.switch_database('mydb')
error = 0
location = "/home/pi/kamera/data/Nowy"
for file in os.listdir(location):
    print("1")
    path = os.path.join(location, file)
    if file.endswith(".json"):
        print(path)
        #otwieram plik
        try:
            with open(path) as f:
                d = []
                d = json.load(f)
                print("przed filtracja")
                print(len(d))
            #przetwarzanie danych: zapis typu, dolnego y, oraz sredniej z x
                json_payload = []              
                for i in range(len(d)):
                    if (len(d[i]["objects"]) > 0):
                        x = (d[i]["objects"][0]["x1"] + d[i]["objects"][0]["x2"])/2
                        y = d[i]["objects"][0]["y1"]
                #przygotowanie danych do wysyłki      
                        if(i>1):          
                            dist = math.sqrt((x-x_old)*(x-x_old)+(y-y_old)*(y-y_old))           
                            if(dist > N):                              
                                data = {
                                        "measurement" : "coordinates",
                                        "time" : datetime.now(),
                                        "fields" : {
                                            "TYPE" : d[i]["objects"][0]["targetType"],
                                            "X" : x,
                                            "Y" : y
                                        }
                                    }
                                x_old = x
                                y_old = y
                                json_payload.append(data)
                        else:
                            data = {
                                        "measurement" : "coordinates",
                                        "time" : datetime.now(),
                                        "fields" : {
                                            "TYPE" : d[i]["objects"][0]["targetType"],
                                            "X" : x,
                                            "Y" : y
                                        }
                                    }
                            x_old = x
                            y_old = y
                            json_payload.append(data)
        except IOError as e:
            error = 1
            print(e)
        finally:
            if(error == 0):
                os.remove(path)
                print("Deleted" + path)
        print("po filtracji")
        print(len(json_payload))
        for x in range(0, len(json_payload), 500):
            chunks = []
            chunks = json_payload[x:x+500]
            client.write_points(chunks)
            
print("koniec")                
