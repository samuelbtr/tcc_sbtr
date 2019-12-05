import paho.mqtt.client as mqtt
import json
import random

''' device_methods = {"get_presence": {"KEY": 1, "REQ": {}, "RES": {"presence": {"PAR": 0, "TYP": "BLN"}}}, 
 "get_lighting": {"KEY": 2, "REQ": {}, "RES": {"lighting": {"PAR": 0, "TYP": "INT", "MIN": 0, "MAX": 1024}}}, 
 "get_PI": {"KEY": 3, "REQ": {}, "RES": {"presence": {"PAR": 0, "TYP": "BLN"}, "lighting": {"PAR": 1, "TYP": "INT", 
 "MIN": 0, "MAX": 1024}}}}'''

device_json = {"ACUPI": {"slave": {"get_presence": {"KEY": 6,
                                                    "REQ": {},
                                                    "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                            "presence": {"PAR": "1", "TYP": "BLN"}}},
                                   "get_lighting": {"KEY": 7,
                                                    "REQ": {},
                                                    "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                            "lighting": {"PAR": "1", "TYP": "INT", "MIN": 0, "MAX": 255}}},
                                   "get_PI": {"KEY": 8,
                                              "REQ": {},
                                              "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                      "presence": {"PAR": "1", "TYP": "BLN"},
                                                      "lighting": {"PAR": "2", "TYP": "INT", "MIN": 0, "MAX": 4095}}}}}}

config = {"broker": "192.168.10.112", "SSID_name": "LSE", "SSID_key": "HubLS3s2", "id": "2"}
id_list = {"master": "1", "slave": []}


def on_message(client, userdata, message):
    #print("message received  ", str(message.payload.decode("utf-8")), "topic", message.topic, "retained ", message.retain)
    m = str(message.payload.decode("utf-8"))
    task(m)


def task(msg):
    global id_list
    global device_json

    response = dict()
    command = json.loads(msg)

    response["s"] = command["m"]

    if command["m"] == device_json["ACUPI"]["slave"]["get_presence"]["KEY"]:
        response[device_json["ACUPI"]["slave"]["get_presence"]["RES"]["id"]["PAR"]] = config["id"]
        response[device_json["ACUPI"]["slave"]["get_presence"]["RES"]["presence"]["PAR"]] = get_presence()

    if command["m"] == device_json["ACUPI"]["slave"]["get_lighting"]["KEY"]:
        response[device_json["ACUPI"]["slave"]["get_lighting"]["RES"]["id"]["PAR"]] = config["id"]
        response[device_json["ACUPI"]["slave"]["get_lighting"]["RES"]["lighting"]["PAR"]] = get_lighting()

    elif command["m"] == device_json["ACUPI"]["slave"]["get_PI"]["KEY"]:
        response.update(get_pi())

    elif command["m"] == 0:
        if command["f"] == 0:
            print("Enviando: ", json.dumps({"s": 0, "f": 0, "0": device_json}))
            client.publish("0", json.dumps({"s": 0, "f": 0, "0": device_json}))
            # print("Enviando: ", json.dumps({"s": 0, "f": 0, "0": {"ACUPA": device_json["ACUPI"]}}))
            # client.publish("0", json.dumps({"s": 0, "f": 0, "0": {"ACUPA": device_json["ACUPI"]}}))
        elif command["f"] == 1:
            device_json = command["0"]
            print("Nova configuração recebida", device_json)
        elif command["f"] == 2:
            id_list["master"] = command["0"]
            print("Mestre alterado: ", id_list["master"])
        elif command["f"] == 3:
            id_list["slave"].append(command["0"])
            print("Slave adicionado: ", command["0"])
            print("Slave cadastrados: ", id_list["slave"])
        return 1
    else:
        response["w"] = "metodo invalido"
        return 0
    print(id_list["master"], json.dumps(response))
    client.publish(id_list["master"], json.dumps(response))


def get_presence():
    return bool(random.randint(0, 1))


def get_lighting():
    return random.randint(0, 255)


def get_pi():
    buffer = dict()
    buffer[device_json["ACUPI"]["slave"]["get_PI"]["RES"]["id"]["PAR"]] = config["id"]
    buffer[device_json["ACUPI"]["slave"]["get_PI"]["RES"]["presence"]["PAR"]] = get_presence()
    buffer[device_json["ACUPI"]["slave"]["get_PI"]["RES"]["lighting"]["PAR"]] = get_lighting()
    return buffer


client = mqtt.Client(config["id"])
client.on_message = on_message

client.connect(config["broker"])
client.subscribe(config["id"])

while True:
    client.loop()
