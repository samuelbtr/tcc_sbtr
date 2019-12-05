import paho.mqtt.client as mqtt
import json
import random
import math

# device_methods = {"get_ON/OFF": {"KEY": 1, "REQ": {}, "RES": {"ON/OFF": {"PAR": 0, "TYP": "BLN"}}}, "set_ON/OFF": {"KEY": 2, "REQ": {"ON/OFF": {"PAR": 0, "TYP": "BLN"}}, "RES": {}}, "get_dimmer": {"KEY": 3, "REQ": {}, "RES": {"dimmer": {"PAR": 0, "TYP": "INT", "MIN": 0, "MAX": 255}}}, "set_dimmer": {"KEY": 4, "REQ": {"dimmer": {"PAR": 0, "TYP": "INT", "MIN": 0, "MAX": 255}}, "RES": {}}, "get_phase": {"KEY": 5, "REQ": {}, "RES": {"phase": {"PAR": 0, "TYP": "CHR", "PMT": ["R", "S", "T"]}}}, "set_phase": {"KEY": 6, "REQ": {"phase": {"PAR": 0, "TYP": "CHR", "PMT": ["R", "S", "T"]}}, "RES": {}}, "get_power": {"KEY": 7, "REQ": {}, "RES": {"power": {"PAR": 0, "TYP": "DBL", "MIN": 0}}}, "get_ILUM": {"KEY": 8, "REQ": {}, "RES": {"ON/OFF": {"PAR": 0, "TYP": "BLN"}, "dimmer": {"PAR": 1, "TYP": "INT", "MIN": 0, "MAX": 255}, "phase": {"PAR": 2, "TYP": "DBL", "MIN": 0}, "power": {"PAR": 3, "TYP": "DBL", "MIN": 0}}}}
# device_name = "001/ILUM"
try:
    import os
    from pyfase import MicroService
except Exception as e:
    print('require module exception: %s' % e)
    exit(0)


class ACUSB(MicroService):
    def __init__(self):
        super(ACUSB, self).__init__(self, sender_endpoint='ipc:///tmp/sender', receiver_endpoint='ipc:///tmp/receiver')

        '''self.device_json = {"ACUSB": {"slave": {"get_energy_parameters": {"KEY": 2,
                                                                          "REQ": {},
                                                                          "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                                                  "avrms": {"PAR": "1",
                                                                                            "TYP": "DOB"},
                                                                                  "bvrms": {"PAR": "2",
                                                                                            "TYP": "DOB"},
                                                                                  "cvrms": {"PAR": "3",
                                                                                            "TYP": "DOB"},
                                                                                  "airms": {"PAR": "4",
                                                                                            "TYP": "DOB"},
                                                                                  "birms": {"PAR": "5",
                                                                                            "TYP": "DOB"},
                                                                                  "cirms": {"PAR": "6",
                                                                                            "TYP": "DOB"},
                                                                                  "apf": {"PAR": "7", "TYP": "DOB"},
                                                                                  "bpf": {"PAR": "8", "TYP": "DOB"},
                                                                                  "cpf": {"PAR": "9", "TYP": "DOB"},
                                                                                  "ava": {"PAR": "10", "TYP": "DOB"},
                                                                                  "bva": {"PAR": "11", "TYP": "DOB"},
                                                                                  "cva": {"PAR": "12", "TYP": "DOB"},
                                                                                  "awatt": {"PAR": "13",
                                                                                            "TYP": "DOB"},
                                                                                  "bwatt": {"PAR": "14",
                                                                                            "TYP": "DOB"},
                                                                                  "cwatt": {"PAR": "15",
                                                                                            "TYP": "DOB"},
                                                                                  "avar": {"PAR": "16",
                                                                                           "TYP": "DOB"},
                                                                                  "bvar": {"PAR": "17",
                                                                                           "TYP": "DOB"},
                                                                                  "cvar": {"PAR": "18",
                                                                                           "TYP": "DOB"},
                                                                                  "awatth": {"PAR": "19",
                                                                                             "TYP": "DOB"},
                                                                                  "bwatth": {"PAR": "20",
                                                                                             "TYP": "DOB"},
                                                                                  "cwatth": {"PAR": "21",
                                                                                             "TYP": "DOB"}}},
                                                "set_ON/OFF": {"KEY": 1,
                                                               "REQ": {"id": {"PAR": "0", "TYP": "STR"},
                                                                       "ON/OFF": {"PAR": "1", "TYP": "BLN"}},
                                                               "RES": {}},
                                                "set_dimmer": {"KEY": 3,
                                                               "REQ": {"id": {"PAR": "0", "TYP": "STR"},
                                                                       "dimmer": {"PAR": "1", "TYP": "INT", "MIN": 0,
                                                                                  "MAX": 255}},
                                                               "RES": {}},
                                                "set_phase": {"KEY": 4,
                                                              "REQ": {"id": {"PAR": "0", "TYP": "STR"},
                                                                      "phase": {"PAR": "1", "TYP": "CHR",
                                                                                "PMT": ["R", "S", "T"]}},
                                                              "RES": {}},
                                                "get_ILUM": {"KEY": 5,
                                                             "REQ": {},
                                                             "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                                     "ON/OFF": {"PAR": "1", "TYP": "BLN"},
                                                                     "dimmer": {"PAR": "2", "TYP": "INT", "MIN": 0,
                                                                                "MAX": 255},
                                                                     "phase": {"PAR": "3", "TYP": "CHR",
                                                                               "PMT": ["R", "S", "T"]},
                                                                     "power": {"PAR": "4", "TYP": "DBL", "MIN": 0}}},
                                                "get_PI": {"KEY": 8,
                                                           "REQ": {},
                                                           "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                                   "presence": {"PAR": "1", "TYP": "BLN"},
                                                                   "lighting": {"PAR": "2", "TYP": "INT", "MIN": 0,
                                                                                "MAX": 1023}}}},
                                      "master": {"set_ON/OFF": {"KEY": 1,
                                                                "REQ": {"ON/OFF": {"PAR": "0", "TYP": "BLN"}},
                                                                "RES": {}},
                                                 "get_dimmer": {"KEY": 2,
                                                                "REQ": {},
                                                                "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                                        "dimmer": {"PAR": "1", "TYP": "INT",
                                                                                   "MIN": 0, "MAX": 255}}},
                                                 "set_dimmer": {"KEY": 3,
                                                                "REQ": {
                                                                    "dimmer": {"PAR": "0", "TYP": "INT", "MIN": 0,
                                                                               "MAX": 255}},
                                                                "RES": {}},
                                                 "set_phase": {"KEY": 4,
                                                               "REQ": {"phase": {"PAR": "0", "TYP": "CHR",
                                                                                 "PMT": ["A", "B", "C"]}},
                                                               "RES": {}},
                                                 "get_ILUM": {"KEY": 5,
                                                              "REQ": {},
                                                              "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                                      "ON/OFF": {"PAR": "1", "TYP": "BLN"},
                                                                      "dimmer": {"PAR": "2", "TYP": "INT", "MIN": 0,
                                                                                 "MAX": 255},
                                                                      "phase": {"PAR": "3", "TYP": "CHR",
                                                                                "PMT": ["A", "B", "C"]},
                                                                      "power": {"PAR": "4", "TYP": "DBL",
                                                                                "MIN": 0}}},
                                                 "get_presence": {"KEY": 6,
                                                                  "REQ": {},
                                                                  "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                                          "presence": {"PAR": "1", "TYP": "BLN"}}},
                                                 "get_lighting": {"KEY": 7,
                                                                  "REQ": {},
                                                                  "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                                          "lighting": {"PAR": "1", "TYP": "INT",
                                                                                       "MIN": 0, "MAX": 4095}}},
                                                 "get_PI": {"KEY": 8,
                                                            "REQ": {},
                                                            "RES": {"id": {"PAR": "0", "TYP": "STR"},
                                                                    "presence": {"PAR": "1", "TYP": "BLN"},
                                                                    "lighting": {"PAR": "2", "TYP": "INT", "MIN": 0,
                                                                                 "MAX": 4095}}}}}}'''

        f = open("device.json")
        self.device_json = json.loads(f.read())
        f.close()

        f = open("config.json")
        self.config = json.loads(f.read())
        f.close()

        f = open("id_list.json")
        self.id_list = json.loads(f.read())
        f.close()
        
        print("configurações: ", self.config)
        print("id_list: ", self.id_list)  
        
        # self.config = {"broker": "192.168.0.29", "SSID_name": "LSE", "SSID_key": "HubLS3s2", "id": "1"}
        #self.id_list = {"master": "", "slave": ["1"]}

        self.client = mqtt.Client(self.config["id"])
        self.client.on_message = self.on_message

        self.client.connect(self.config["broker"])
        self.client.subscribe(self.config["id"])

        self.trasnlateFlag = False
        self.request_action("update_devices", {'devices': self.id_list['slave']})

    def on_message(self, client, userdata, message):
        m = str(message.payload.decode("utf-8"))
        command = json.loads(m)
        print(command)

        if "m" in command:
            self.request_task(command)
        else:
            self.response_task(command)

    def request_task(self, command):

        response = dict()
        # command = json.loads(msg)

        response["m"] = command["m"]
        if command["m"] == self.device_json["ACUSB"]["slave"]["set_ON/OFF"]["KEY"]:
            self.set_on_off(self.device_json["ACUSB"]["master"]["set_ON/OFF"]["KEY"],
                            command[self.device_json["ACUSB"]["slave"]["set_ON/OFF"]["REQ"]["id"]["PAR"]],
                            command[self.device_json["ACUSB"]["slave"]["set_ON/OFF"]["REQ"]["ON/OFF"]["PAR"]])

        elif command["m"] == self.device_json["ACUSB"]["slave"]["set_dimmer"]["KEY"]:
            self.request_action("get_alarme", {})
            self.set_dimmer(self.device_json["ACUSB"]["master"]["set_dimmer"]["KEY"],
                            command[self.device_json["ACUSB"]["slave"]["set_dimmer"]["REQ"]["id"]["PAR"]],
                            command[self.device_json["ACUSB"]["slave"]["set_dimmer"]["REQ"]["dimmer"]["PAR"]])

        elif command["m"] == self.device_json["ACUSB"]["slave"]["set_phase"]["KEY"]:
            self.set_phase(self.device_json["ACUSB"]["master"]["set_phase"]["KEY"],
                           command[self.device_json["ACUSB"]["slave"]["set_phase"]["REQ"]["id"]["PAR"]],
                           command[self.device_json["ACUSB"]["slave"]["set_phase"]["REQ"]["phase"]["PAR"]])

        elif command["m"] == self.device_json["ACUSB"]["slave"]["get_ILUM"]["KEY"]:
            print(self.device_json["ACUSB"]["slave"]["get_ILUM"]["KEY"])
            self.get_ilum_request(self.device_json["ACUSB"]["master"]["get_ILUM"]["KEY"])

        elif command["m"] == self.device_json["ACUSB"]["slave"]["get_PI"]["KEY"]:
            self.get_pi_request(self.device_json["ACUSB"]["master"]["get_PI"]["KEY"])

        elif command["m"] == self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["KEY"]:
            self.get_energy_parameters()
            # self.request_action("measurement", {})

        elif command["m"] == 0:
            if command["f"] == 0:
                print("Enviando: ", json.dumps({"s": 0, "f": 0, "0": self.device_json}))
                self.client.publish("0", json.dumps({"s": 0, "f": 0, "0": self.device_json}))
                # print("Enviando: ", json.dumps({"s": 0, "f": 0, "0": {"ACUSA": device_json["ACUSB"]}}))
                # client.publish("0", json.dumps({"s": 0, "f": 0, "0": {"ACUSA": device_json["ACUSB"]}}))
            elif command["f"] == 1:
                self.device_json = json.loads(command["0"])
                f = open("device.json", "w")
                f.write(json.dumps(self.device_json))
                f.close()
                print("Nova configuração recebida", device_json)
            elif command["f"] == 2:
                self.id_list["master"] = command["0"]
                f = open("id_list.json", "w")
                f.write(json.dumps(self.id_list))
                f.close()
                print("Mestre alterado: ", self.id_list["master"])
            elif command["f"] == 3:
                if command["0"] not in self.id_list["slave"]:
                    self.id_list["slave"].append(command["0"])
                    print("adicionando slaves: ", self.id_list)
                    f = open("id_list.json", "w")
                    f.write(json.dumps(self.id_list))
                    f.close()
                    print("Slave adicionado: ", command["0"])
                print("Slave cadastrados: ", self.id_list["slave"])
            return 1
        else:
            response["w"] = "metodo invalido"
            # self.client.publish(config["master"], json.dumps(response))

    def response_task(self, command):

        response = dict()
        # command = json.loads(msg)
        response["s"] = command["s"]

        if command["s"] == self.device_json["ACUSB"]["master"]["get_ILUM"]["KEY"]:
            self.get_ilum_response(self.device_json["ACUSB"]["slave"]["get_ILUM"]["KEY"],
                                   command[self.device_json["ACUSB"]["master"]["get_ILUM"]["RES"]["id"]["PAR"]],
                                   command[self.device_json["ACUSB"]["master"]["get_ILUM"]["RES"]["ON/OFF"]["PAR"]],
                                   command[self.device_json["ACUSB"]["master"]["get_ILUM"]["RES"]["dimmer"]["PAR"]],
                                   command[self.device_json["ACUSB"]["master"]["get_ILUM"]["RES"]["phase"]["PAR"]],
                                   command[self.device_json["ACUSB"]["master"]["get_ILUM"]["RES"]["power"]["PAR"]])

        elif command["s"] == self.device_json["ACUSB"]["slave"]["get_PI"]["KEY"]:
            self.get_pi_response(self.device_json["ACUSB"]["slave"]["get_PI"]["KEY"],
                                 command[self.device_json["ACUSB"]["master"]["get_PI"]["RES"]["id"]["PAR"]],
                                 command[self.device_json["ACUSB"]["master"]["get_PI"]["RES"]["presence"]["PAR"]],
                                 command[self.device_json["ACUSB"]["master"]["get_PI"]["RES"]["lighting"]["PAR"]])

        elif command["s"] == 0:
            if command["f"] == 0:
                print("Enviando: ", json.dumps({"s": 0, "f": 0, "0": self.device_json}))
                self.client.publish("0", json.dumps({"s": 0, "f": 0, "0": self.device_json}))
                # print("Enviando: ", json.dumps({"s": 0, "f": 0, "0": {"ACUSA": device_json["ACUSB"]}}))
                # client.publish("0", json.dumps({"s": 0, "f": 0, "0": {"ACUSA": device_json["ACUSB"]}}))
            elif command["f"] == 1:
                device_json = json.loads(command["0"])
                print("Nova configuração recebida", device_json)
            elif command["f"] == 2:
                self.id_list["master"] = command["0"]
                print("Mestre alterado: ", self.id_list["master"])
            elif command["f"] == 3:
                self.id_list["slave"].append(json.loads(command["0"]))
                print("Slave adicionado: ", command["0"])
                print("Slave cadastrados: ", self.id_list["slave"])
            return 1
        else:
            response["w"] = "metodo invalido"
            return 0

    def set_on_off(self, key, id_device, state):
        request = dict()
        request["m"] = key
        request[self.device_json["ACUSB"]["master"]["set_ON/OFF"]["REQ"]["ON/OFF"]["PAR"]] = state

        self.client.publish(id_device, json.dumps(request))

    def set_dimmer(self, key, id_device, value):
        request = dict()
        request["m"] = key
        request[self.device_json["ACUSB"]["master"]["set_dimmer"]["REQ"]["dimmer"]["PAR"]] = value
        self.client.publish(id_device, json.dumps(request))

    def set_phase(self, key, id_device, phase):
        request = dict()
        request["m"] = key
        request[self.device_json["ACUSB"]["master"]["set_phase"]["REQ"]["phase"]["PAR"]] = phase
        self.client.publish(id_device, json.dumps(request))

    def get_ilum_request(self, key):
        request = dict()
        request["m"] = key

        for device in self.id_list["slave"]:
            self.client.publish(device, json.dumps(request))

    def get_pi_request(self, key):
        request = dict()
        request["m"] = key
        for device in self.id_list["slave"]:
            self.client.publish(device, json.dumps(request))

    def get_ilum_response(self, key, id_device, state, dimmer, phase, power):
        response = dict()
        response["s"] = key
        response[self.device_json["ACUSB"]["slave"]["get_ILUM"]["RES"]["id"]["PAR"]] = id_device
        response[self.device_json["ACUSB"]["slave"]["get_ILUM"]["RES"]["ON/OFF"]["PAR"]] = state
        response[self.device_json["ACUSB"]["slave"]["get_ILUM"]["RES"]["dimmer"]["PAR"]] = dimmer
        response[self.device_json["ACUSB"]["slave"]["get_ILUM"]["RES"]["phase"]["PAR"]] = phase
        response[self.device_json["ACUSB"]["slave"]["get_ILUM"]["RES"]["power"]["PAR"]] = power

        self.request_action("update_devices", {'devices': self.id_list['slave']})
        self.request_action("get_all_slave", {"ilum": dimmer, "id": id_device})
        self.client.publish(self.id_list["master"], json.dumps(response))

    def get_pi_response(self, key, id_device, presence, lighting):
        response = dict()
        response["s"] = key
        response[self.device_json["ACUSB"]["slave"]["get_PI"]["RES"]["id"]["PAR"]] = id_device
        response[self.device_json["ACUSB"]["slave"]["get_PI"]["RES"]["presence"]["PAR"]] = presence
        response[self.device_json["ACUSB"]["slave"]["get_PI"]["RES"]["lighting"]["PAR"]] = lighting
        self.client.publish(self.id_list["master"], json.dumps(response))
        self.request_action("update_devices", {'devices': self.id_list['slave']})
        print("aqui: ", {"presence": presence, "lighting": lighting})
        self.request_action("get_all_slave", {"presence": presence, "lighting": lighting})

    def get_energy_parameters(self):
        response = dict()
        v = 126.8 + random.randint(0, 4)/10
        i = (0.2 + random.randint(0, 10)/100.0)*4
        fp = 0.915 + random.randint(0, 10) / 1000.0
        t = 5/3600

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["id"]["PAR"]] = self.config["id"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["avrms"]["PAR"]] = v
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bvrms"]["PAR"]] = 0
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cvrms"]["PAR"]] = 0

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["airms"]["PAR"]] = i
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["birms"]["PAR"]] = 0
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cirms"]["PAR"]] = 0

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["apf"]["PAR"]] = fp
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bpf"]["PAR"]] = 1
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cpf"]["PAR"]] = 1

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["ava"]["PAR"]] = v*i
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bva"]["PAR"]] = 0
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cva"]["PAR"]] = 0

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["awatt"]["PAR"]] = v*i*fp
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bwatt"]["PAR"]] = 0
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cwatt"]["PAR"]] = 0

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["avar"]["PAR"]] = v*i*math.sin(math.acos(fp))
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bvar"]["PAR"]] = 0
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cvar"]["PAR"]] = 0

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["awatth"]["PAR"]] = v*i*fp*t
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bwatth"]["PAR"]] = 0
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cwatth"]["PAR"]] = 0

        print(response)
        self.client.publish(self.id_list["master"], json.dumps(response))
        #self.request_action("measurement", {})

    @MicroService.action
    def get_all_master(self, service, data):
        print(data)
        self.get_ilum_request(self.device_json["ACUSB"]["master"]["get_ILUM"]["KEY"])
        self.get_pi_request(self.device_json["ACUSB"]["master"]["get_PI"]["KEY"])

    @MicroService.action
    def set_dimmer_action(self, service, data):
        print(data)
        self.set_dimmer(self.device_json["ACUSB"]["master"]["set_dimmer"]["KEY"], data["id"], data["value"])

    @MicroService.action
    def mqtt_publish(self, service, data):
        response = dict()
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["id"]["PAR"]] = self.config["id"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["avrms"]["PAR"]] = data["avrms"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bvrms"]["PAR"]] = data["bvrms"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cvrms"]["PAR"]] = data["cvrms"]

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["airms"]["PAR"]] = data["airms"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["birms"]["PAR"]] = data["birms"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cirms"]["PAR"]] = data["cirms"]

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["apf"]["PAR"]] = data["apf"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bpf"]["PAR"]] = data["bpf"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cpf"]["PAR"]] = data["cpf"]

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["ava"]["PAR"]] = data["ava"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bva"]["PAR"]] = data["bva"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cva"]["PAR"]] = data["cva"]

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["awatt"]["PAR"]] = data["awatt"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bwatt"]["PAR"]] = data["bwatt"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cwatt"]["PAR"]] = data["cwatt"]

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["avar"]["PAR"]] = data["avar"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bvar"]["PAR"]] = data["bvar"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cvar"]["PAR"]] = data["cvar"]

        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["awatth"]["PAR"]] = data["awatth"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["bwatth"]["PAR"]] = data["bwatth"]
        response[self.device_json["ACUSB"]["slave"]["get_energy_parameters"]["RES"]["cwatth"]["PAR"]] = data["cwatth"]
        print(response)
        self.client.publish(self.id_list["master"], json.dumps(response))

    @MicroService.task
    def main_loop(self):
        self.client.loop_forever()


ACUSB().execute(enable_tasks=True)
