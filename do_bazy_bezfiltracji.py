import json
import os
import sys
import math
from datetime import datetime
from influxdb import InfluxDBClient
from dateutil.relativedelta import relativedelta
client = InfluxDBClient('localhost', 8086, 'admin', 'Password1', 'mydb')
client.switch_database('mydb')

location = "/home/pi/kamera/data/Nowy"
for file in os.listdir(location):
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
                        x = d[i]["objects"][0]["X"]
                        y = d[i]["objects"][0]["Y"]
                #przygotowanie danych do wysyłki      
                        if(i>1):          
                            #dist = math.sqrt((x-x_old)*(x-x_old)+(y-y_old)*(y-y_old))           
                            #if(dist > N):                              
                            data = {
                                "measurement" : "coordinates",
                                "time" : datetime.now() + relativedelta(years=1),
                                "fields" : {
                                    "TYPE" : d[i]["objects"][0]["targetType"],
                                    "X" : x,
                                    "Y" : y
                                }
                            }
                        #x_old = x
                        #y_old = y
                            json_payload.append(data)
                        else:
                            data = {
                                        "measurement" : "coordinates",
                                        "time" : datetime.now() + relativedelta(years=1),
                                        "fields" : {
                                            "TYPE" : d[i]["objects"][0]["targetType"],
                                            "X" : x,
                                            "Y" : y
                                        }
                                    }
                            #x_old = x
                            #y_old = y
                            json_payload.append(data)
        except IOError as e:
            error = 1
            print(e)
        #finally:
            #if(error == 0):
                #os.remove(path)
                #print("Deleted" + path)
        print("po filtracji")
        print(len(json_payload))
        for x in range(0, len(json_payload), 500):
            chunks = []
            chunks = json_payload[x:x+500]
            client.write_points(chunks)
            
print("koniec")                