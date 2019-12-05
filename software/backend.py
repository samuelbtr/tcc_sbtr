import json
import paho.mqtt.client as mqtt
from pyfase import MicroService


class Backend(MicroService):
    def __init__(self):
        super(Backend, self).__init__(self, sender_endpoint='ipc:///tmp/sender',
                                        receiver_endpoint='ipc:///tmp/receiver')

        f = open("appConfig.json", "r")
        self.config = json.loads(f.read())
        f.close()

        f = open("structure.json", "r")
        self.structure = json.loads(f.read())
        f.close()

        self.client = mqtt.Client(self.config["id"])
        self.client.on_message = self.on_message

        self.client.connect(self.config["broker"])
        self.client.subscribe(self.config["id"])

        self.newDevice = dict()

    def saveDevice(self, device):
        pass

    def on_message(self, client, userdata, message):
        command = json.loads(str(message.payload.decode("utf-8")))
        print("Recebida resposta do novo dispositivo")
        if command["s"] == 0:
            if command["f"] == 0:
                # newDevice = {"caminho": ["ACUSB"], "name": "ACUPI", "id": "4"}
                # print(self.deviceExist(self.structure, "ACULUM"))
                #newDevice = {"way": ["ACUSB"], "name": "ACUPA", "id": "4"}

                newDevice = self.newDevice
                self.newDevice["type"] = list(command["0"].keys())[0]
                print("Novo dispositivo: ", self.newDevice)
                newDeviceBuffer = self.structure
                for device in self.newDevice["way"]:
                    newDeviceBuffer = newDeviceBuffer[device]

                idConfig = self.typeExist(newDeviceBuffer, self.newDevice["type"])
                if idConfig != "":
                    newDeviceBuffer[self.newDevice["id"]] = {"config": newDeviceBuffer[idConfig]["config"], "type": self.newDevice["type"]}
                    print("Novo dipositivo: ", self.newDevice["id"], newDeviceBuffer[self.newDevice["id"]])

                    f = open("configs/" + newDeviceBuffer[idConfig]["config"] + ".json", "r")
                    configSend = f.read()
                    f.close()

                    configSend = configSend.replace("\n", "")
                    configSend = configSend.replace(" ", "")
                    print("Nova configuração enviada para o dispositivo: ", configSend)
                    self.client.publish(self.newDevice["id"], json.dumps({"m": 0, "f": 1, "0": json.loads(configSend)}))
                    self.request_action("status", {"status": "cadastro concluido", "structure": self.structure})
                else:
                    configListBuffer = list()
                    self.configList(self.structure, configListBuffer)
                    i = 1
                    while str(i) in configListBuffer:
                        i += 1
                    newDeviceBuffer[self.newDevice["id"]] = {"config": str(i), "type": self.newDevice["type"]}

                    print("Nova configuração sendo salva: ", json.dumps(command["0"][self.newDevice["type"]]))
                    print("No cominho: ", "configs/" + str(i) + ".json")
                    f = open("configs/" + str(i) + ".json", "w")
                    f.write(json.dumps(command["0"]))
                    f.close()

                    print("new device buffer: ", newDeviceBuffer)
                    if "config" in newDeviceBuffer:
                        f = open("configs/" + newDeviceBuffer["config"] + ".json", "r")
                        masterConfig = json.loads(f.read())
                        f.close()
                        print("master config: ", masterConfig)
                        masterConfig[list(masterConfig)[0]].pop("slave")
                        self.request_action("link", {"slave": command["0"], "master": masterConfig})
                        #self.request_action("statusInfo", {"status": "cadastro parcialmente concluido"})
                    else:
                        self.request_action("status", {"status": "cadastro concluido", "structure": self.structure})

                if len(newDevice["way"]) > 0:
                    print("Enviando para o master %s o slave %s"%(self.newDevice["way"][-1], self.newDevice["id"]))
                    self.client.publish(self.newDevice["way"][-1], json.dumps({"m": 0, "f": 3, "0": self.newDevice["id"]}))
                    print("Enviando para o slave %s o master %s" % (self.newDevice["id"], self.newDevice["way"][-1]))
                    self.client.publish(self.newDevice["id"], json.dumps({"m": 0, "f": 2, "0": self.newDevice["way"][-1]}))

                f = open("structure.json", "w")
                f.write(json.dumps(self.structure))
                f.close()
                print("Novo valor de structure: ", self.structure)
                print("\n\n")

    @staticmethod
    def typeExist(newDeviceBuffer, newDeviceType):
        for deviceId in newDeviceBuffer:
            if deviceId != "type" and deviceId != "config":
                if newDeviceBuffer[deviceId]["type"] == newDeviceType:
                    return deviceId
        return ""

    def on_connect(self):
        print('### on_connect ###')

    def on_new_service(self, service, actions):
        print('### on_new_service ### service: %s - actions: %s' % (service, actions))

    def on_response(self, service, data):
        print('### on_response ### service: %s respond an status of the action save_data previous resquested: %s' % (
            service, data))

    '''def idExist(self, devices, newId):
        if newId in devices["ids"]:
            return True
        for device in devices:
            if device != "ids" and device != "config":
                if self.idExist(devices[device], newId):
                    return True
        return False'''

    def idList(self, devices, deviceList):
        deviceList += list(devices.keys())
        for device in devices:
            if device != "type" and device != "config":
                self.idList(devices[device], deviceList)

    '''def deviceExist(self, devices, newDevice):
        for device in devices:
            if device != "ids" and device != "config":
                if device == newDevice:
                    return True
                else:
                    if self.deviceExist(devices[device], newDevice):
                        return True
        return False'''

    def configList(self, devices, deviceList):
        for device in devices:
            if device != "type" and device != "config":
                deviceList += devices[device]["config"]
                self.configList(devices[device], deviceList)

    @MicroService.action
    def requestNewDeviceId(self, service, data):
        deviceList = list()
        self.idList(self.structure, deviceList)
        i = 1
        while str(i) in deviceList:
            i += 1
        self.request_action("newId", {"id": str(i)})

    @MicroService.action
    def getNewDevice(self, service, data):
        print("Enviando requisição mqtt")
        self.newDevice = dict(data)
        self.client.publish(data["id"], json.dumps({"m": 0, "f": 0}))

    @MicroService.action
    def linkRegister(self, service, data):
        print("Salvando e enviando nova configuração: ", data)

        f = open("configs/" + self.newDevice["id"]+".json", "w")
        f.write(json.dumps(data["slave"]))
        f.close()

        newDeviceBuffer = self.structure
        for device in self.newDevice["way"]:
            newDeviceBuffer = newDeviceBuffer[device]

        if "config" in newDeviceBuffer:
            f = open("configs/" + newDeviceBuffer["config"] + ".json", "r")
            masterConfig = json.loads(f.read())
            f.close()

            masterConfig["master"] = data["master"]

            f = open("configs/" + newDeviceBuffer["config"] + ".json", "w")
            f.write(json.dumps(masterConfig))
            f.close()

        self.request_action("status", {"status": "cadastro concluido", "structure": self.structure})

        print("Enviando configuração...")
        self.client.publish(self.newDevice["id"], json.dumps({"m": 0, "f": 1, "0": data["slave"]}))
        if "config" in newDeviceBuffer:
            self.client.publish(self.newDevice["way"][-1], json.dumps({"m": 0, "f": 1, "0": data["master"]}))
        print("Configuração enviada", data, "\n\n")

    @MicroService.task
    def main_loop(self):
        self.client.loop_forever()


Backend().execute(enable_tasks=True)
