from pymongo import MongoClient
import pymongo.errors as mongoerr
from serial.tools import list_ports
import serial
import time
from datetime import datetime
 
 
def find_port():
    ports = list_ports.comports()
    for port in ports:
        if port.manufacturer == "FTDI":
            print("checking ", port.device)
            s = serial.Serial(port.device, 115200, timeout=3)
            message = "~"
            s.write(message.encode())
 
            response = s.readline()
            response = response.decode().strip()
 
            s.close()
            print(f'close {port.device}')
 
            if (response == "Elka"):
                print("port found\n")
                return port.device
 
            else:
                print("not correct port\n")
 
 
def open_port():
    comport_name = find_port()
    print("port is", comport_name)
    s = serial.Serial(comport_name, 115200, timeout=2)
    print("port open")
    return s
 
 
def open_mongo():
    client = MongoClient(
        host="roboforge.ru",
        username="admin",
        password="pinboard123",
        authSource="admin",
        serverSelectionTimeoutMS=5000,
        socketTimeoutMS=2000
    )
    return client
 
 
def get_value():
    try:
        message = "&"
        s.write(message.encode())
        response = s.readline()
        value = int(response.decode().strip())
        print("recived: ", value, end="    ")
        return value
 
    except (ValueError, UnicodeDecodeError) as e:
        print("get value error: ", e)
        return None
 
def send_temp_records():
    global client
    global TEMPDATA
    if (len(TEMPDATA) != 0):
        print("\n tempdata started saving")
        for record in TEMPDATA:
            try:
                coll.insert_one(record)
            except (
                mongoerr.DuplicateKeyError, mongoerr.WriteError,
                mongoerr.BulkWriteError, mongoerr.InvalidId,
                mongoerr.WriteConcernError, UnicodeDecodeError) as e:
                print(f"write error, don't save record from temp\n record: {record}\n error: \t {e}")
                client = open_mongo()
                print("\nreopened mongo\n")
        print("tempdata saved\n")
        TEMPDATA = []
 
def send_record(record):
    global client
    global TEMPDATA
    try:
        coll.insert_one(record)
        print(f"\tsent: {record['datetime']} {record['value']}")
 
    except (
        mongoerr.DuplicateKeyError,
        mongoerr.WriteError,
        mongoerr.BulkWriteError,
        mongoerr.InvalidId,
        mongoerr.WriteConcernError,
        UnicodeDecodeError
        ) as e:
        print("write error, don't save record, error: \n", e)
        client = open_mongo()
        print("\nreopened mongo\n")
 
 
    except (
        mongoerr.NetworkTimeout,
        mongoerr.ServerSelectionTimeoutError,
        mongoerr.ExecutionTimeout,
        mongoerr.AutoReconnect,
        UnicodeDecodeError) as e:
        TEMPDATA.append(record)
        print("save record, stoped with error: \n", e)
        client = open_mongo()
        print("\nreopened mongo\n")
 
 
 
TEMPDATA = []
 
client = open_mongo()
print(client.list_database_names())
db = client["chernogor"]
coll = db["photoresistor"]
 
# while True:
#     try:
        
while True:
    try:
        s = open_port()
        while True:
 
            dt = datetime.now()
            if dt.second == 0:
                value = get_value()
                if value:
                    record = {"datetime": dt, "value": value}
 
                    send_record(record)
 
                    send_temp_records()
                time.sleep(40)
            time.sleep(0.4)
    except (serial.serialutil.SerialException, UnicodeDecodeError) as e:
        print("wait 10 secs, error: ", e)
        time.sleep(10)
    except (mongoerr.AutoReconnect, UnicodeDecodeError) as e:
        print("autoreconect\t", e)
        client = open_mongo()
        print("tried to connect")
    # except (mongoerr.AutoReconect, UnicodeDecodeError as e):
    #     client = open_mongo()
    #     print("\nreopened mongo\n")
 
    # sleep(40)
 
