# coding=utf-8
__author__ = 'jmorais, Samuel Torres'

try:
    import os
    import sys

    sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
    from pyfase import Fase, MicroService
    import json
    import time
    from subprocess import getoutput
except Exception as e:
    print('require module exception: %s' % e)
    exit(0)


class Wifi(MicroService):
    def __init__(self):
        super(Wifi, self).__init__(self, sender_endpoint='ipc:///tmp/sender', receiver_endpoint='ipc:///tmp/receiver')
        self.interface = "mlan0"
        self.settings_path = "/etc"
        self.broker = "192.168.10.112"

    def on_connect(self):
        print('### on_connect ###')

    def on_broadcast(self, service, data):
        print('### on_broadcast ### service: %s - data: %s' % (service, data))

    def on_new_service(self, service, actions):
        print('### on_new_service ### service: %s - actions: %s' % (service, actions))

    def on_response(self, service, data):
        print('### on_response ### service: %s - actions: %s' % (service, data))

    @staticmethod
    def wpa_supplicant_stop():
        for tries in range(0, 10):
            pid = getoutput('pidof wpa_supplicant')
            if len(pid) > 0:
                os.system('kill -9 %s' % str(pid))
            else:
                return True
            time.sleep(1)
        return False

    @staticmethod
    def get_wifi_interface():
        ret = getoutput('ifconfig | grep mlan').split()
        interface = ''
        n = len(ret)
        if n > 0:
            interface = ret[0]
        else:
            for i in range(0, 10):
                os.system('ifconfig mlan%s up &' % i)
        return interface

    def wpa_supplicant_start(self):
        interface = self.get_wifi_interface()
        os.system('ifconfig %s down' % interface)
        if self.wpa_supplicant_stop():
            os.system('wpa_supplicant -P /var/run/wpa_supplicant.%s.pid -i %s -D nl80211,wext -c %s/wpa_supplicant.conf &' % (interface, interface, self.settings_path))
            time.sleep(10)
            pid = getoutput('pidof wpa_supplicant')
            if len(pid) > 0:
                return True
        return False

    @staticmethod
    def dhcp_stop():
        instances = getoutput('pidof udhcpc')
        for trie in range(0, 5):
            if len(instances) > 0:
                os.system('kill -9 %s' % instances)
                time.sleep(1)
            else:
                return True
        return False

    def dhcp_start(self, interface):
        self.dhcp_stop()
        os.system('udhcpc -i %s' % interface)
        time.sleep(3)

    def connect(self):
        if self.wpa_supplicant_start():
            self.dhcp_start(self.get_wifi_interface())
            for tries in range(0, 20):
                time.sleep(1)
                ret = getoutput('ifconfig %s | grep "inet addr"' % self.get_wifi_interface())
                if len(ret) > 0:
                    return True, ret.split()[1][5:]
                ret = getoutput('ifconfig %s | grep "inet"' % self.get_wifi_interface())
                if len(ret) > 0:
                    return True, ret.split()[1]
        return False, ''

    def wifi_connect(self):
        print('WIFI CONECTANDO...')
        if self.wpa_supplicant_start():
            status, ip = self.connect()
            if status:
                print('WIFI CONECTADO! IP: %s' % ip)
                return True
            else:
                print('NAO CONECTOU!!!')
                return False
        else:
            print('NAO INICIOU O WPA_SUPPLICANT!!!')
            return False

    def connected(self):
        ret = getoutput('iwconfig %s | grep off/any' % self.interface)
        if len(ret) > 0:
            return False
        return True

    @MicroService.task
    def wifi_task(self):
        self.wifi_connect()
        while True:
            time.sleep(1)
            # gerenciamento da conexão wifi, detecção de quebra de conexão
            if self.connected():
                self.request_action('wifi_status', {'connection_status': 'online'})
            else:
                self.request_action('wifi_status', {'connection_status': 'offline'})
                self.wifi_connect()


Wifi().execute(enable_tasks=True)
