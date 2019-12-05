import paho.mqtt.client as mqtt
import json
import random

# device_methods = {"get_ON/OFF": {"KEY": 1, "REQ": {}, "RES": {"ON/OFF": {"PAR": 0, "TYP": "BLN"}}}, "set_ON/OFF": {"KEY": 2, "REQ": {"ON/OFF": {"PAR": 0, "TYP": "BLN"}}, "RES": {}}, "get_dimmer": {"KEY": 3, "REQ": {}, "RES": {"dimmer": {"PAR": 0, "TYP": "INT", "MIN": 0, "MAX": 255}}}, "set_dimmer": {"KEY": 4, "REQ": {"dimmer": {"PAR": 0, "TYP": "INT", "MIN": 0, "MAX": 255}}, "RES": {}}, "get_phase": {"KEY": 5, "REQ": {}, "RES": {"phase": {"PAR": 0, "TYP": "CHR", "PMT": ["R", "S", "T"]}}}, "set_phase": {"KEY": 6, "REQ": {"phase": {"PAR": 0, "TYP": "CHR", "PMT": ["R", "S", "T"]}}, "RES": {}}, "get_power": {"KEY": 7, "REQ": {}, "RES": {"power": {"PAR": 0, "TYP": "DBL", "MIN": 0}}}, "get_ILUM": {"KEY": 8, "REQ": {}, "RES": {"ON/OFF": {"PAR": 0, "TYP": "BLN"}, "dimmer": {"PAR": 1, "TYP": "INT", "MIN": 0, "MAX": 255}, "phase": {"PAR": 2, "TYP": "DBL", "MIN": 0}, "power": {"PAR": 3, "TYP": "DBL", "MIN": 0}}}}
# device_name = "001/ILUM"

device_json = {"ACULUM": {"slave": {"get_ON/OFF": {"KEY": 9,
                                                  "REQ": {},
                                                  "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                          "ON/OFF": {"PAR": "1", "TYP": "BLN"}}},
                                    "set_ON/OFF": {"KEY": 1,
                                                  "REQ": {"ON/OFF": {"PAR": "0", "TYP": "BLN"}},
                                                  "RES": {}},
                                    "get_dimmer": {"KEY": 2,
                                                   "REQ": {},
                                                   "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                           "dimmer": {"PAR": "1", "TYP": "INT", "MIN": 0, "MAX": 255}}},
                                    "set_dimmer": {"KEY": 3,
                                                   "REQ": {"dimmer": {"PAR": "0", "TYP": "INT", "MIN": 0, "MAX": 255}},
                                                   "RES": {}},
                                    "get_phase": {"KEY": 10,
                                                  "REQ": {},
                                                  "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                          "phase": {"PAR": "1", "TYP": "CHR", "PMT": ["A", "B", "C"]}}},
                                    "set_phase": {"KEY": 4,
                                                  "REQ": {"phase": {"PAR": "0", "TYP": "CHR", "PMT": ["A", "B", "C"]}},
                                                  "RES": {}},
                                    "get_power": {"KEY": 11,
                                                  "REQ": {},
                                                  "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                          "power": {"PAR": "1", "TYP": "DOB", "MIN": 0}}},
                                    "get_ILUM": {"KEY": 5,
                                                  "REQ": {},
                                                  "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                          "ON/OFF": {"PAR": "1", "TYP": "BLN"},
                                                          "dimmer": {"PAR": "2", "TYP": "INT", "MIN": 0, "MAX": 255},
                                                          "phase": {"PAR": "3", "TYP": "CHR", "PMT": ["A", "B", "C"]},
                                                          "power": {"PAR": "4", "TYP": "DBL", "MIN": 0}}}}}}

config = {"broker": "192.168.10.112", "SSID_name": "LSE", "SSID_key": "HubLS3s2", "id": "6"}
id_list = {"master": "1", "slave": []}


def on_message(client, userdata, message):
    m = str(message.payload.decode("utf-8"))
    task(m)



def task(msg):
    global id_list
    global device_json

    response = dict()
    command = json.loads(msg)

    response["s"] = command["m"]
    if command["m"] == device_json["ACULUM"]["slave"]["get_ON/OFF"]["KEY"]:
        response[device_json["ACULUM"]["slave"]["get_ON/OFF"]["RES"]["id"]["PAR"]] = config["id"]
        response[device_json["ACULUM"]["slave"]["get_ON/OFF"]["RES"]["ON/OFF"]["PAR"]] = get_on_off()

    elif command["m"] == device_json["ACULUM"]["slave"]["set_ON/OFF"]["KEY"]:
        set_on_off(command[device_json["ACULUM"]["slave"]["set_ON/OFF"]["REQ"]["ON/OFF"]["PAR"]])

    elif command["m"] == device_json["ACULUM"]["slave"]["get_dimmer"]["KEY"]:
        response[device_json["ACULUM"]["slave"]["get_dimmer"]["RES"]["id"]["PAR"]] = config["id"]
        response[device_json["ACULUM"]["slave"]["get_dimmer"]["RES"]["dimmer"]["PAR"]] = get_dimmer()

    elif command["m"] == device_json["ACULUM"]["slave"]["set_dimmer"]["KEY"]:
        set_dimmer(command[device_json["ACULUM"]["slave"]["set_dimmer"]["REQ"]["dimmer"]["PAR"]])

    elif command["m"] == device_json["ACULUM"]["slave"]["get_phase"]["KEY"]:
        response[device_json["ACULUM"]["slave"]["get_phase"]["RES"]["id"]["PAR"]] = config["id"]
        response[device_json["ACULUM"]["slave"]["get_phase"]["RES"]["phase"]["PAR"]] = get_phase()

    elif command["m"] == device_json["ACULUM"]["slave"]["set_phase"]["KEY"]:
        set_phase(command[device_json["ACULUM"]["slave"]["set_phase"]["REQ"]["phase"]["PAR"]])

    elif command["m"] == device_json["ACULUM"]["slave"]["get_power"]["KEY"]:
        response[device_json["ACULUM"]["slave"]["get_power"]["RES"]["id"]["PAR"]] = config["id"]
        response[device_json["ACULUM"]["slave"]["get_power"]["RES"]["power"]["PAR"]] = get_power()

    elif command["m"] == device_json["ACULUM"]["slave"]["get_ILUM"]["KEY"]:
        response.update(get_ilum())

    elif command["m"] == 0:
        if command["f"] == 0:
            print("Enviando: ", json.dumps({"s": 0, "f": 0, "0": device_json}))
            client.publish("0", json.dumps({"s": 0, "f": 0, "0": device_json}))
            # print("Enviando: ", json.dumps({"s": 0, "f": 0, "0": {"ACULAM": device_json["ACULUM"]}}))
            # client.publish("0", json.dumps({"s": 0, "f": 0, "0": {"ACULAM": device_json["ACULUM"]}}))
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


def get_on_off():
    return bool(random.randint(0, 1))


def set_on_off(state):
    print(state)


def get_dimmer():
    return random.randint(0, 255)


def set_dimmer(value):
    print(value)


def get_phase():
    phase = ["R", "S", "T"]
    return phase[random.randint(0, 2)]


def set_phase(phase):
    print(phase)


def get_power():
    return random.randint(0, 1500) * 0.01


def get_ilum():
    buffer = dict()
    buffer[device_json["ACULUM"]["slave"]["get_ILUM"]["RES"]["id"]["PAR"]] = config["id"]
    buffer[device_json["ACULUM"]["slave"]["get_ILUM"]["RES"]["ON/OFF"]["PAR"]] = get_on_off()
    buffer[device_json["ACULUM"]["slave"]["get_ILUM"]["RES"]["dimmer"]["PAR"]] = get_dimmer()
    buffer[device_json["ACULUM"]["slave"]["get_ILUM"]["RES"]["phase"]["PAR"]] = get_phase()
    buffer[device_json["ACULUM"]["slave"]["get_ILUM"]["RES"]["power"]["PAR"]] = get_power()

    return buffer


client = mqtt.Client(config["id"])
client.on_message = on_message

client.connect(config["broker"])
client.subscribe(config["id"])

while True:
    client.loop()
