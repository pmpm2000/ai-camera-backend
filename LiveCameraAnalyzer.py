# -*- coding: utf-8 -*-
"""
Created on Thu Mar 10 19:24:23 2022

@author: Przemek
"""


import socket, math
from SmartXmlParser import SmartXmlParser, save_responses, send_responses
from influxdb import InfluxDBClient

CAMERA = '192.168.114.163'  # The server's hostname or IP address
PORT = 8080                 # The port used by the server

responses = []

print("Uruchamiam klienta")
#client = InfluxDBClient('localhost', 8086, 'admin', 'Password1', 'mydb')
#client.switch_database('mydb')
request = ""
with open("request_py.txt", 'rb') as f:  # read request file in binary mode to keep correct "end of line" characters
    request = f.read()

limit = 500

while True:
    responses = []
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((CAMERA, PORT))
            print("Podłączony do serwera")

            sxp = SmartXmlParser()

            for i in range(limit):
                #data = bytes(request, "utf-8")        
                s.send(request)
                print("Wysłałem request")

                zakres = 10
                for j in range(zakres):
                    print(f"Odbieram j={j} ----------------")
                    rec = s.recv(10000)
#                     print(rec)
                    rr = rec.decode()
                    print(rr)
                    sxp.add_new_text(rr)
                    print(sxp.frames)
                    for f in sxp.frames:#f to słownik ze struktura danych
                        responses.append(f)
                    print(responses)
                    sxp.frames = []
    except Exception as e:
        print(f"EXCEPTION: {e}")
    finally:
        print(1)
        send_responses(responses)
        