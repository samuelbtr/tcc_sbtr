import json
import paho.mqtt.client as mqtt
from pyfase import MicroService
import time


class Translate(MicroService):
    def __init__(self):
        super(Translate, self).__init__(self, sender_endpoint='ipc:///tmp/sender',
                                        receiver_endpoint='ipc:///tmp/receiver')
        f = open("config.json")
        self.device_json = json.loads(f.read())
        f.close()

        self.id = "translate"

        self.client = mqtt.Client(self.id)
        self.client.on_message = self.on_message

        self.client.connect(self.device_json["broker"])
        self.client.subscribe(self.id + "S")
        self.message_buffer = dict()
        self.devices = list()

        self.request_action("get_all_master", {})

    def on_message(self, client, userdata, message):
        command = json.loads(str(message.payload.decode("utf-8")))  # {"t": "set_dimmer", "id": "ilum1", "value": 125}
        if command["t"] == "get_all":
            self.request_action("get_all_master", {})
        if command["t"] == "set_dimmer":
            print(command, self.devices[int(command["id"][-1]) - 1])
            command.pop("t")
            command["id"] = self.devices[int(command["id"][-1])-1]
            self.request_action("set_dimmer_action", command) #{"value": 125}

    def on_connect(self):
        print('### on_connect ###')

    def on_new_service(self, service, actions):
        print('### on_new_service ### service: %s - actions: %s' % (service, actions))

    def on_response(self, service, data):
        print('### on_response ### service: %s respond an status of the action save_data previous resquested: %s' % (
            service, data))

    @MicroService.action
    def get_all_slave(self, service, data):
        if "id" in data:
            if data["id"] not in self.devices:
                self.devices.append(data["id"])
            data["dimmer" + str(self.devices.index(data.pop("id"))+1)] = data["ilum"]
            data.pop("ilum")
        self.message_buffer.update(data)

    @MicroService.action
    def get_alarme(self, service, data):
        self.request_action("get_all_master", {})

    @MicroService.task
    def update_mqtt(self):
        self.client.loop_forever()

    @MicroService.task
    def get_parameters(self):
        while True:
            while self.message_buffer == {}:
                pass
            time.sleep(5)
            print(self.message_buffer)
            flag = True
            for message in ["presence", "lighting", "ilum1", "ilum2", "ilum3", "ilum4"]:
                if message not in self.message_buffer:
                    flag = False
            if flag:
                self.client.publish(self.id + "P", json.dumps(self.message_buffer))
            self.message_buffer = {}


Translate().execute(enable_tasks=True)
