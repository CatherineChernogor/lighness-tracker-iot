from pymongo import MongoClient
from pymongo.errors import PyMongoError
from serial.tools import list_ports
import serial
import time
from datetime import datetime


def find_port():
    ports = list_ports.comports()
    for port in ports:
        if port.manufacturer == "FTDI":
            print(port.name)
            s = serial.Serial(port.device, 115200, timeout=2)
            message = "~"
            s.write(message.encode())

            response = s.readline()
            response = response.decode().strip()
            print(response)

            s.close()
            print(f'close {port.device} \n')

            if (response == "Elka"):
                print("port found")
                return port.device

            else:
                print("not correct port")


def open_port():
    comport_name = find_port()
    print("port is", comport_name)
    s = serial.Serial(comport_name, 115200, timeout=2)
    print("port open")
    return s


client = MongoClient(
    host="roboforge.ru",
    username="admin",
    password="pinboard123",
    authSource="admin",
    serverSelectionTimeoutMS=5000,
    socketTimeoutMS=2000
)
print(client.list_database_names())
db = client["chernogor"]
coll = db["photoresistor"]

tempdata = []

while True:

    try:
        s = open_port()
        while True:
            try:
                message = "&"
                s.write(message.encode())
                response = s.readline()
                print(response)

                value = int(response.decode().strip())

            except ValueError:
                break

            dt = datetime.now()
            if dt.second % 10 == 0:
                record = {"datetime": dt, "value": value}
                print(record)

                try:
                    if (len(tempdata) != 0):
                        coll.insert_many(tempdata)
                        print("upload saved")
                        tempdata = []

                    coll.insert_one(record)
                except PyMongoError:

                    tempdata.append(record)
                    print("save")

                time.sleep(6)
            time.sleep(0.7)
    except (serial.serialutil.SerialException, UnicodeDecodeError) as e:
        print("wait 10 secs", e)
        time.sleep(10)
