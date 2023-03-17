# -*- coding: utf-8 -*-
"""
Created on Tue Mar 15 18:07:30 2022

@author: Przemek
"""

import xml.etree.ElementTree as ET
import json, time, math
from datetime import datetime
from influxdb import InfluxDBClient

ns = {'ns': 'http://www.ipc.com/ver10'}   # default namespace declared by the camera

def send_responses(responses, N = 30):
    print("przedfiltracja "+str(len(responses)))
    client = InfluxDBClient('localhost', 8086, 'admin', 'Password1', 'mydb')
    client.switch_database('mydb')
    json_payload = []
    x_old = 0
    y_old = 0
    if(len(responses)>0):
        for i in range(len(responses)):
            if (len(responses[i]["objects"]) > 0):
                x = (responses[i]["objects"][0]["x1"] + responses[i]["objects"][0]["x2"])/2
                y = responses[i]["objects"][0]["y1"]
                if(i>1):          
                    dist = math.sqrt((x-x_old)*(x-x_old)+(y-y_old)*(y-y_old))           
                    if(dist > N):                              
                        data = {
                                "measurement" : "coordinates",
                                "time" : datetime.now(),
                                "fields" : {
                                    "TYPE" : responses[i]["objects"][0]["targetType"],
                                    "X" : x,
                                    "Y" : y
                                    }
                                }
                        x_old = x
                        y_old = y
                        json_payload.append(data)
                elif(i == 0):
                    data = {
                            "measurement" : "coordinates",
                            "time" : datetime.now(),
                                "fields" : {
                                "TYPE" : responses[i]["objects"][0]["targetType"],
                                "X" : x,
                                "Y" : y
                                }
                            }
                    x_old = x
                    y_old = y
                    json_payload.append(data)
        print("pofiltracji "+str(len(json_payload)))
        for x in range(0, len(json_payload), 500):
                chunks = []
                chunks = json_payload[x:x+500]
                client.write_points(chunks)
def save_responses(responses):
    fn = time.strftime("%Y%m%d-%H%M%S")
    full_fn = f"detected_objects_{fn}.json"
    print(f"---------------- saving results to file: {full_fn} ---------------------")
    with open(full_fn, 'w') as f:
        json.dump(responses, f, indent=4, sort_keys=True)

def save_debug_string(s):
    fn = time.strftime("%Y%m%d-%H%M%S")
    full_fn = f"debug_{fn}.txt"
    print("SAVE debug info")
    with open(full_fn, 'w') as f:
        f.write(s)    

class SmartXmlParser:
    
    def __init__(self):
        self.last_text = ""
        self.to_be_parsed = ""
        self.xml_docs = []
        self.frames = []
    
    # Method accepts new text to be parsed (it can be mixed with HTTP response headers and may be incomplete XML)
    def add_new_text(self, text):
        self.last_text = text
        watchdog = 5
        if text.find("POST /") == 0:
            self.to_be_parsed = text
        else:
            self.to_be_parsed += text
        
        while True:
            self.to_be_parsed = self.__strip_http_headers(self.to_be_parsed)
            single_xml_document = self.to_be_parsed
            post_idx = self.to_be_parsed.find("POST /")  # find begin of a next message - it may not exist
            if post_idx!=-1:
                single_xml_document = self.to_be_parsed[0:post_idx]
            try:
                #print(single_xml_document)
                tree = ET.fromstring(single_xml_document)
                self.xml_docs.append(tree)
                self.to_be_parsed = self.to_be_parsed[post_idx:]
        #        print(post_idx, self.to_be_parsed, "-----")
            except Exception as e:
                print(e)
            print(".")
            if self.to_be_parsed.find("POST /")==-1:
                break
            watchdog -= 1
            if (watchdog==0):
                print("WATCHDOG break!")
                break
        
        for xd in self.xml_docs:
            self.__extractVideoData(xd)
    
    
    def __extractVideoData(self, xml_doc):
        frame = {"info" : {}, "objects": []}   # empty description of a new video frame 
        li = xml_doc.find("ns:listInfo", ns)
        if (li != None):
            try:
                # TODO: decode frame info here
                
                items = li.findall("*")
                for item in items:
                    detectedObject = {}
                    detectedObject['targetId'] = item.find("ns:targetId", ns).text
                    #data = str(datetime.now())
                    #detectedObject['date'] = data[0:]
                    rect = item.find("ns:rect", ns)
                    for r in rect:
                        bidx = r.tag.index("}") + 1
                        key = r.tag[bidx:]    # remove namespace
                        detectedObject[key] = int(r.text)
                        
                    
                    tid = item.find("ns:targetImageData", ns)
                    tt = tid.find("ns:targetType", ns)
                    detectedObject['targetType'] = int(tt.text)
                    frame["objects"].append(detectedObject)
                    
            except Exception as e:
                msg = f"Exception: {e}    DATA: {xml_doc}"
                print("-----------", msg)
                frame["info"]["exception"] = msg
            if (len(frame['objects'])==0):    # there exist frames with listInfo, but they result in no objects detected - WHY?
                print("!!!!!! Frame without objects !!!!!!")   # save_debug_string(self.last_text)    
            self.frames.append(frame)


    def __strip_http_headers(self, s):
        post_idx = s.find("POST /")
        xml_idx = s.find("<?xml")
        print(post_idx, xml_idx)
        ret = s
        if (xml_idx!=-1):
            ret = s[xml_idx:]
        return ret  



if __name__=="__main__":
    
    testdata1 = """POST /SendAlarmData HTTP/1.1 
    
<?xml version="1.0" encoding="UTF-8" ?><config version="1.7" xmlns="http://www.ipc.com/ver10"><types><smartType><enum>MOTION</enum><enum>SENSOR</enum><enum>PERIMETER</enum><enum>TRIPWIRE</enum><enum>PEA</enum><enum>AVD</enum><enum>OSC</enum><enum>CPC</enum><enum>CDD</enum><enum>IPD</enum><enum>VFD</enum><enum>VEHICE</enum><enum>AOIENTRY</enum><enum>AOILEAVE</enum><enum>PASSLINECOUNT</enum><enum>TRAFFIC</enum></smartType><subscribeOption><enum>ALARM</enum><enum>FEATURE_RESULT</enum><enum>FEATURE_RULE</enum></subscribeOption><smartStatus><enum>SMART_NONE</enum><enum>SMART_START</enum><enum>SMART_STOP</enum><enum>SMART_PROCEDURE</enum></smartStatus></types><smartType type="openAlramObj">PASSLINECOUNT</smartType><subscribeRelation type="subscribeOption">FEATURE_RESULT</subscribeRelation><currentTime type="tint64">1647363695604787</currentTime><passLineCount><enterCarCount type="uint32">129</enterCarCount><enterPersonCount type="uint32">2400</enterPersonCount><enterBikeCount type="uint32">41</enterBikeCount><leaveCarCount type="uint32">426</leaveCarCount><leavePersonCount type="uint32">2397</leavePersonCount><leaveBikeCount type="uint32">25</leaveBikeCount><existCarCount type="uint32">0</existCarCount><existPersonCount type="uint32">0</existPersonCount><existBikeCount type="uint32">0</existBikeCount><aoiInfo type="list" count="1"><item><eventId type="uint32">103042</eventId><targetId type="uint32">102442</targetId><status type="smartStatus">SMART_START</status><line><x1 type="uint32">40</x1><y1 type="uint32">9866</y1><x2 type="uint32">9880</x2><y2 type="uint32">2506</y2><!-- 1, ANY_DIRECTION; 2, LEFT_TO_RIGHT 3,RIGHT_TO_LEFT --><Direct type="uint32">2</Direct></line><rect><x1 type="uint32">2329</x1><y1 type="uint32">5902</y1><x2 type="uint32">5255</x2><y2 type="uint32">9548</y2></rect></item></aoiInfo></passLineCount><sourceDataInfo><!-- 0, JPG; 1, YUV --><dataType type="uint32">0</dataType><width type="uint32">0</width><height type="uint32">0</height><!-- Length of encrypted source data Base64 --><sourceBase64Length type="uint32">0</sourceBase64Length><!-- Base64 Encryption of Source Data --><sourceBase64Data type="string"><![CDATA[]]></sourceBase64Data></sourceDataInfo><listInfo type="list" count="1"><item><targetId type="tuint32">102442</targetId><rect><x1 type="uint32">2329</x1><y1 type="uint32">5902</y1><x2 type="uint32">5255</x2><y2 type="uint32">9548</y2></rect><targetImageData><!-- 0, JPG; 1, YUV --><dataType type="uint32">0</dataType><!-- 1:person;2:car;4:bike--><targetType type="uint32">1</targetType><Width type="tuint32">0</Width><Height type="tuint32">0</Height><!-- Length of encrypted face data Base64 --><targetBase64Length type="uint32">0</targetBase64Length><!-- Base64 Encryption of face Data --><targetBase64Data type="string"><![CDATA[]]></targetBase64Data></targetImageData></item></listInfo></config>POST /SendAlarmData HTTP/1.1Host: 192.168.114.163Content-Length:3067Content-Type:application/xml; charset=utf-8Connection: keep-alive<?xml version="1.0" encoding="UTF-8" ?><config version="1.7" xmlns="http://www.ipc.com/ver10"><types><smartType><enum>MOTION</enum><enum>SENSOR</enum><enum>PERIMETER</enum><enum>TRIPWIRE</enum><enum>PEA</enum><enum>AVD</enum><enum>OSC</enum><enum>CPC</enum><enum>CDD</enum><enum>IPD</enum><enum>VFD</enum><enum>VEHICE</enum><enum>AOIENTRY</enum><enum>AOILEAVE</enum><enum>PASSLINECOUNT</enum><enum>TRAFFIC</enum></smartType><subscribeOption><enum>ALARM</enum><enum>FEATURE_RESULT</enum><enum>FEATURE_RULE</enum></subscribeOption><smartStatus><enum>SMART_NONE</enum><enum>SMART_START</enum><enum>SMART_STOP</enum><enum>SMART_PROCEDURE</enum></smartStatus></types><smartType type="openAlramObj">PASSLINECOUNT</smartType><subscribeRelation type="subscribeOption">FEATURE_RESULT</subscribeRelation><currentTime type="tint64">1647363695627191</currentTime><passLineCount><enterCarCount type="uint32">129</enterCarCount><enterPersonCount type="uint32">2400</enterPersonCount><enterBikeCount type="uint32">41</enterBikeCount><leaveCarCount type="uint32">426</leaveCarCount><leavePersonCount type="uint32">2397</leavePersonCount><leaveBikeCount type="uint32">25</leaveBikeCount><existCarCount type="uint32">0</existCarCount><existPersonCount type="uint32">0</existPersonCount><existBikeCount type="uint32">0</existBikeCount><aoiInfo type="list" count="1"><item><eventId type="uint32">103042</eventId><targetId type="uint32">102442</targetId><status type="smartStatus">SMART_START</status><line><x1 type="uint32">40</x1><y1 type="uint32">9866</y1><x2 type="uint32">9880</x2><y2 type="uint32">2506</y2><!-- 1, ANY_DIRECTION; 2, LEFT_TO_RIGHT 3,RIGHT_TO_LEFT --><Direct type="uint32">2</Direct></line><rect><x1 type="uint32">2329</x1><y1 type="uint32">5902</y1><x2 type="uint32">5255</x2><y2 type="uint32">9548</y2></rect></item></aoiInfo></passLineCount><sourceDataInfo><!-- 0, JPG; 1, YUV --><dataType type="uint32">0</dataType><width type="uint32">0</width><height type="uint32">0</height><!-- Length of encrypted source data Base64 --><sourceBase64Length type="uint32">0</sourceBase64Length><!-- Base64 Encryption of Source Data --><sourceBase64Data type="string"><![CDATA[]]></sourceBase64Data></sourceDataInfo><listInfo type="list" count="1"><item><targetId type="tuint32">102442</targetId><rect><x1 type="uint32">2329</x1><y1 type="uint32">5902</y1><x2 type="uint32">5255</x2><y2 type="uint32">9548</y2></rect><targetImageData><!-- 0, JPG; 1, YUV --><dataType type="uint32">0</dataType><!-- 1:person;2:car;4:bike--><targetType type="uint32">1</targetType><Width type="tuint32">0</Width><Height type="tuint32">0</Height><!-- Length of encrypted face data Base64 --><targetBase64Length type="uint32">0</targetBase64Length><!-- Base64 Encryption of face Data --><targetBase64Data type="string"><![CDATA[]]></targetBase64Data></targetImageData></item></listInfo></config>POST /SendAlarmData HTTP/1.1Host: 192.168.114.163Content-Length:3067Content-Type:application/xml; charset=utf-8Connection: keep-alive<?xml version="1.0" encoding="UTF-8" ?><config version="1.7" xmlns="http://www.ipc.com/ver10"><types><smartType><enum>MOTION</enum><enum>SENSOR</enum><enum>PERIMETER</enum><enum>TRIPWIRE</enum><enum>PEA</enum><enum>AVD</enum><enum>OSC</enum><enum>CPC</enum><enum>CDD</enum><enum>IPD</enum><enum>VFD</enum><enum>VEHICE</enum><enum>AOIENTRY</enum><enum>AOILEAVE</enum><enum>PASSLINECOUNT</enum><enum>TRAFFIC</enum></smartType><subscribeOption><enum>ALARM</enum><enum>FEATURE_RESULT</enum><enum>FEATURE_RULE</enum></subscribeOption><smartStatus><enum>SMART_NONE</enum><enum>SMART_START</enum><enum>SMART_STOP</enum><enum>SMART_PROCEDURE</enum></smartStatus></types><smartType type="openAlramObj">PASSLINECOUNT</smartType><subscribeRelation type="subscribeOption">FEATURE_RESULT</subscribeRelation><currentTime type="tint64">1647363695670784</currentTime><passLineCount><enterCarCount type="uint32">129</enterCarCount><enterPersonCount type="uint32">2400</enterPersonCount><enterBikeCount type="uint32">41</enterBikeCount><leaveCarCount type="uint32">426</leaveCarCount><leavePersonCount type="uint32">2397</leavePersonCount><leaveBikeCount type="uint32">25</leaveBikeCount><existCarCount type="uint32">0</existCarCount><existPersonCount type="uint32">0</existPersonCount><existBikeCount type="uint32">0</existBikeCount><aoiInfo type="list" count="1"><item><eventId type="uint32">103042</eventId><targetId type="uint32">102442</targetId><status type="smartStatus">SMART_START</status><line><x1 type="uint32">40</x1><y1 type="uint32">9866</y1><x2 type="uint32">9880</x2><y2 type="uint32">2506</y2><!-- 1, ANY_DIRECTION; 2, LEFT_TO_RIGHT 3,RIGHT_TO_LEFT --><Direct type="uint32">2</Direct></line><rect><x1 type="uint32">2357</x1><y1 type="uint32">5937</y1><x2 type="uint32">5227</x2><y2 type="uint32">9548</y2></rect></item></aoiInfo></passLineCount><sourceDataInfo><!-- 0, JPG; 1, YUV --><dataType type="uint32">0</dataType><width type="uint32">0</width><height type="uint32">0</height><!-- Length of encrypted source data Base64 --><sourceBase64Length type="uint32">0</sourceBase64Length><!-- Base64 Encryption of Source Data --><sourceBase64Data type="string"><![CDATA[]]></sourceBase64Data></sourceDataInfo><listInfo type="list" count="1"><item><targetId type="tuint32">102442</targetId><rect><x1 type="uint32">2357</x1><y1 type="uint32">5937</y1><x2 type="uint32">5227</x2><y2 type="uint32">9548</y2></rect><targetImageData><!-- 0, JPG; 1, YUV --><dataType type="uint32">0</dataType><!-- 1:person;2:car;4:bike--><targetType type="uint32">1</targetType><Width type="tuint32">0</Width><Height type="tuint32">0</Height><!-- Length of encrypted face data Base64 --><targetBase64Length type="uint32">0</targetBase64Length><!-- Base64 Encryption of face Data --><targetBase64Data type="string"><![CDATA[]]></targetBase64Data></targetImageData></item></listInfo></config>POST /SendAlarmData HTTP/1.1Host: 192.168.114.163Content-Length:3067Content-Type:application/xml; charset=utf-8Connection: keep-alive<?xml version="1.0" encoding="UTF-8" ?><config version="1.7" xmlns="http://www.ipc.com/ver10"><types><smartType><enum>MOTION</enum><enum>SENSOR</enum><enum>PERIMETER</enum><enum>TRIPWIRE</enum><enum>PEA</enum><enum>AVD</enum><enum>OSC</enum><enum>CPC</enum><enum>CDD</enum><enum>IPD</enum><enum>VFD</enum><enum>VEHICE</enum><enum>AOIENTRY</enum><enum>AOILEAVE</enum><enum>PASSLINECOUNT</enum><enum>TRAFFIC</enum></smartType><subscribeOption><enum>ALARM</enum><enum>FEATURE_RESULT</enum><enum>FEATURE_RULE</enum></subscribeOption><smartStatus><enum>SMART_NONE</enum><enum>SMART_START</enum><enum>SMART_STOP</enum><enum>SMART_PROCEDURE</enum></smartStatus></types><smartType type="openAlramObj">PASSLINECOUNT</smartType><subscribeRelation type="subscribeOption">FEATURE_RESULT</subscribeRelation><currentTime type="tint64">1647363695712666</currentTime><passLineCount><enterCarCount type="uint32">129</enterCarCount><enterPersonCount type="uint32">2400</enterPersonCount><enterBikeCount type="uint32">41</enterBikeCount><leaveCarCount type="uint32">426</leaveCarCount><leavePersonCount type="uint32">2397</leavePersonCount><leaveBikeCount type="uint32">25</leaveBikeCount><existCarCount type="uint32">0</existCarCount><existPersonCount type="uint32">0</existPersonCount><existBikeCount type="uint32">0</existBikeCount><aoiInfo type="list" count="1"><item><eventId type="uint32">103042</eventId><targetId type="uint32">102442</targetId><status type="smartStatus">SMART_START</status><line><x1 type="uint32">40</x1><y1 type="uint32">9866</y1><x2 type="uint32">9880</x2><y2 type="uint32">2506</y2><!-- 1, ANY_DIRECTION; 2, LEFT_TO_RIGHT 3,RIGHT_TO_LEFT --><Direct type="uint32">2</Direct></line><rect><x1 type="uint32">2357</x1><y1 type="uint32">5937</y1><x2 type="uint32">5227</x2><y2 type="uint32">9548</y2></rect></item></aoiInfo></passLineCount><sourceDataInfo><!-- 0, JPG; 1, YUV --><dataType type="uint32">0</dataType><width type="uint32">0</width><height type="uint32">0</height><!-- Length of encrypted source data Base64 --><sourceBase64Length type="uint32">0</sourceBase64Length><!-- Base64 Encryption of Source Data --><sourceBase64Data type="string"><![CDATA[]]></sourceBase64Data></sourceDataInfo><listInfo type="list" count="1"><item><targetId type="tuint32">102442</targetId><rect><x1 type="uint32">2357</x1><y1 type="uint32">5937</y1><x2 type="uint32">5227</x2><y2 type="uint32">9548</y2></rect><targetImageData><!-- 0, JPG; 1, YUV --><dataType type="uint32">0</dataType><!-- 1:person;2:car;4:bike--><targetType type="uint32">1</targetType><Width type="tuint32">0</Width><Height type="tuint32">0</Height><!-- Length of encrypted face data Base64 --><targetBase64Length type="uint32">0</targetBase64Length><!-- Base64 Encryption of face Data --><targetBase64Data type="string"><![CDATA[]]></targetBase64Data></targetImageData></item></listInfo></config>"""

    sxp = SmartXmlParser()
    
    sxp.add_new_text(testdata1)
    print(len(sxp.xml_docs))
    print(len(sxp.frames))
    send_responses(sxp.frames)
    for do in sxp.frames:
        print(do)
    
    
    
