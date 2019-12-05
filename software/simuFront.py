import json
import paho.mqtt.client as mqtt
from pyfase import MicroService
import time


class SimuFronte(MicroService):
    def __init__(self):
        super(SimuFronte, self).__init__(self, sender_endpoint='ipc:///tmp/sender',
                                        receiver_endpoint='ipc:///tmp/receiver')

        f = open("appConfig.json", "r")
        config = json.loads(f.read())
        f.close()

        self.client = mqtt.Client(config["id"])
        self.client.on_message = self.on_message

        self.client.connect(config["broker"])
        self.client.subscribe(config["id"])

        self.idBuffer = str()
        self.devicesToLink = dict()

    @staticmethod
    def on_message(client, userdata, message):
        command = json.loads(str(message.payload.decode("utf-8")))

    def on_connect(self):
        pass
        #print('### on_connect ###')

    def on_new_service(self, service, actions):
        print('### on_new_service ### service: %s - actions: %s' % (service, actions))

    def on_response(self, service, data):
        print('### on_response ### \nservice: %s \nresquested: %s' % (service, data))

    @MicroService.action
    def newId(self, service, data):
        print("\nid: " + data["id"])
        self.idBuffer = data["id"]

    @MicroService.action
    def status(self, service, data):
        print(data["status"])

    @MicroService.action
    def link(self, service, data):
        print("slave: ", data["slave"])
        print("master: ", data["master"])

        self.devicesToLink = data

    @MicroService.task
    def do_anything(self):
        while True:
            t = input("\ntask: ")
            if t == "1":
                self.request_action("requestNewDeviceId", {})
            elif t == "2":
                self.request_action("linkRegister", self.devicesToLink)
            elif t == "10":
                self.request_action("getNewDevice", {"id": self.idBuffer, "way": []})
            elif t == "20":
                self.request_action("getNewDevice", {"id": self.idBuffer, "way": ["1"]})
            elif t == "21":
                self.devicesToLink["slave"]["ACUPI"]["slave"]["get_presence"]["KEY"] = 88
            elif t == "30":
                self.request_action("getNewDevice", {"id": self.idBuffer, "way": ["1"]})
            elif t == "31":
                print(self.devicesToLink)
                self.devicesToLink["slave"]["ACULUM"]["slave"]["get_ON/OFF"]["KEY"] = 88

            time.sleep(1)


SimuFronte().execute(enable_tasks=True)
