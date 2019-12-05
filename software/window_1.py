from tkinter import *
from tkinter import messagebox
import json
from pyfase import MicroService
import threading


class ScrollFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        self.canvas = Canvas(self, borderwidth=0, background="#222222")          #place canvas on self
        self.viewPort = Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets
        self.vsb = Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the viewPort frame changes.

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.

class App(threading.Thread):
    def __init__(self, tk_root):
        self.fase = Application(tk_root)
        threading.Thread.__init__(self)
        self.daemon = True
        self.start()

    def run(self):
        self.fase.execute(enable_tasks=True)


class Application(MicroService):
    def __init__(self, master=None):
        super(Application, self).__init__(self, sender_endpoint='ipc:///tmp/sender', receiver_endpoint='ipc:///tmp/receiver')

        f = open("structure.json", "r")
        self.structure = json.loads(f.read())
        f.close()

        self.slave = {'ACUPI': {'slave': {'get_presence': {'KEY': 6, 'REQ': {}, 'RES': {'id': {'PAR': '0', 'TYP': 'STR'}, 'presence': {'PAR': '1', 'TYP': 'BLN'}}}, 'get_lighting': {'KEY': 7, 'REQ': {}, 'RES': {'id': {'PAR': '0', 'TYP': 'STR'}, 'lighting': {'PAR': '1', 'TYP': 'INT', 'MIN': 0, 'MAX': 1023}}}, 'get_PI': {'KEY': 8, 'REQ': {}, 'RES': {'id': {'PAR': '0', 'TYP': 'STR'}, 'presence': {'PAR': '1', 'TYP': 'BLN'}, 'lighting': {'PAR': '2', 'TYP': 'INT', 'MIN': 0, 'MAX': 1023}}}}}}
        self.master = {'ACUSB': {'master': {'set_ON/OFF': {'KEY': 1, 'REQ': {'ON/OFF': {'PAR': '0', 'TYP': 'BLN'}}, 'RES': {}}, 'get_dimmer': {'KEY': 2, 'REQ': {}, 'RES': {'id': {'PAR': '0', 'TYP': 'STR'}, 'dimmer': {'PAR': '1', 'TYP': 'INT', 'MIN': 0, 'MAX': 255}}}, 'set_dimmer': {'KEY': 3, 'REQ': {'dimmer': {'PAR': '0', 'TYP': 'INT', 'MIN': 0, 'MAX': 255}}, 'RES': {}}, 'set_phase': {'KEY': 4, 'REQ': {'phase': {'PAR': '0', 'TYP': 'CHR', 'PMT': ['R', 'S', 'T']}}, 'RES': {}}, 'get_ILUM': {'KEY': 5, 'REQ': {}, 'RES': {'id': {'PAR': '0', 'TYP': 'STR'}, 'ON/OFF': {'PAR': '1', 'TYP': 'BLN'}, 'dimmer': {'PAR': '2', 'TYP': 'INT', 'MIN': 0, 'MAX': 255}, 'phase': {'PAR': '3', 'TYP': 'CHR', 'PMT': ['R', 'S', 'T']}, 'power': {'PAR': '4', 'TYP': 'DBL', 'MIN': 0}}}, 'get_presence': {'KEY': 6, 'REQ': {}, 'RES': {'id': {'PAR': '0', 'TYP': 'STR'}, 'presence': {'PAR': '1', 'TYP': 'BLN'}}}, 'get_lighting': {'KEY': 7, 'REQ': {}, 'RES': {'id': {'PAR': '0', 'TYP': 'STR'}, 'lighting': {'PAR': '1', 'TYP': 'INT', 'MIN': 0, 'MAX': 1023}}}, 'get_PI': {'KEY': 8, 'REQ': {}, 'RES': {'id': {'PAR': '0', 'TYP': 'STR'}, 'presence': {'PAR': '1', 'TYP': 'BLN'}, 'lighting': {'PAR': '2', 'TYP': 'INT', 'MIN': 0, 'MAX': 1023}}}}}}

        self.masterBuffer = dict()
        self.slaveBuffer = dict()
        self.entryBuffer = dict()

        self.masterWindow = master
        self.masterWindow.geometry("960x960")

        self.windowComponents = dict()
        self.linkComponents = dict()

        self.newDevice = dict()
        self.newDevice["way"] = list()

        self.idBuffer = str()

        self.structBuffer = self.structure

        self.windowWay()

        #self.linkScreen()

    @staticmethod
    def on_message(client, userdata, message):
        command = json.loads(str(message.payload.decode("utf-8")))

    def on_connect(self):
        pass
        # print('### on_connect ###')

    def on_new_service(self, service, actions):
        print('### on_new_service ### service: %s - actions: %s' % (service, actions))

    def on_response(self, service, data):
        print('### on_response ### \nservice: %s \nresquested: %s' % (service, data))

    def windowWay(self):
        for component in self.structBuffer:
            if component != "type" and component != "config":
                self.windowComponents[component] = Button(self.masterWindow, text=self.structBuffer[component]["type"]+"/"+component, command=lambda way=component: self.addWay(way))
                self.windowComponents[component].pack()
        if len(self.newDevice["way"]) > 0:
            self.windowComponents["voltar"] = Button(self.masterWindow, text="Voltar", command=lambda: self.voltar())
            self.windowComponents["voltar"].pack()
        self.windowComponents["adicionar"] = Button(self.masterWindow, text="Adicionar Dispositivo", command=lambda: self.request_id())
        self.windowComponents["adicionar"].pack()

    def addWay(self, way):
        self.newDevice["way"].append(way)
        self.structBuffer = self.structBuffer[way]
        for component in self.windowComponents:
            self.windowComponents[component].destroy()
        # print("windowWay: ", self.windowComponents)
        self.windowWay()
        # print("\n", self.newDevice, "\n", self.structBuffer, "\n")

    def voltar(self):
        self.newDevice["way"] = self.newDevice["way"][:-1]
        self.structBuffer = self.structure
        for way in self.newDevice["way"]:
            self.structBuffer = self.structBuffer[way]
        for component in self.windowComponents:
            self.windowComponents[component].destroy()
        # print("windowWay: ", self.windowComponents)
        self.windowWay()

    def request_id(self):
        self.request_action("requestNewDeviceId", {})

    def linkScreen(self):
        self.masterBuffer = self.master[list(self.master)[0]]["master"]
        self.slaveBuffer = self.slave[list(self.slave)[0]]["slave"]

        self.linkComponents["slave"] = dict()
        self.linkComponents["master"] = dict()

        self.entryBuffer["slave"] = dict()
        self.entryBuffer["master"] = dict()

        self.linkComponents["slave"]["scrollFrame"] = ScrollFrame(self.masterWindow)
        self.linkComponents["slave"]["frame/slave"] = Frame(self.linkComponents["slave"]["scrollFrame"].viewPort)
        self.linkComponents["slave"]["label/slave"] = Label(self.linkComponents["slave"]["frame/slave"], text="Slave "+list(self.slave)[0], font=("Verdana", "24", "italic", "bold"), bg="purple")
        self.linkComponents["slave"]["frame/slave"].pack(side=RIGHT, fill=BOTH, expand=True)
        self.linkComponents["slave"]["label/slave"].pack(fill=BOTH, expand=True)

        for method in self.slaveBuffer:
            self.linkComponents["slave"]["frame/" + method] = Frame(self.linkComponents["slave"]["frame/slave"], highlightbackground="black", highlightthickness=1, bg="green")
            self.linkComponents["slave"]["box1/" + method] = Frame(self.linkComponents["slave"]["frame/" + method], highlightbackground="black", highlightthickness=1, bg="green")
            self.linkComponents["slave"]["Label/" + method] = Label(self.linkComponents["slave"]["box1/" + method], text=method, bg="green", font=("Verdana", "16", "italic", "bold"))

            self.entryBuffer["slave"][method] = dict()
            self.entryBuffer["slave"][method]["KEY"] = Entry(self.linkComponents["slave"]["box1/" + method], bg="blue", font=("Verdana", "14", "italic"), justify='center')
            self.entryBuffer["slave"][method]["KEY"].insert(0, self.slaveBuffer[method]["KEY"])

            self.linkComponents["slave"]["frame/" + method].pack(fill=BOTH, expand=True)
            self.linkComponents["slave"]["box1/" + method].pack(side=LEFT, fill=BOTH, expand=True)
            self.linkComponents["slave"]["Label/" + method].pack(fill=BOTH, expand=True)
            self.entryBuffer["slave"][method]["KEY"].pack(fill=X, expand=True)

            self.linkComponents["slave"]["box2/" + method] = Frame(self.linkComponents["slave"]["frame/" + method], highlightbackground="black", highlightthickness=1, bg="orange")
            self.linkComponents["slave"]["box2/" + method].pack(side=RIGHT, fill=BOTH, expand=True)

            if self.slaveBuffer[method]["REQ"] != {}:
                self.linkComponents["slave"]["request/" + method] = Label(self.linkComponents["slave"]["box2/" + method], text="REQUESTS", font=("Verdana", "16", "italic", "bold"))
                self.linkComponents["slave"]["request/" + method].pack(fill=BOTH, expand=True)
            self.entryBuffer["slave"][method]["REQ"] = dict()
            for parameter in self.slaveBuffer[method]["REQ"]:
                self.linkComponents["slave"]["Label/" + method + parameter] = Label(self.linkComponents["slave"]["box2/" + method], text=parameter, bg="orange", font=("Verdana", "16", "italic", "bold"))

                self.entryBuffer["slave"][method]["REQ"][parameter] = Entry(self.linkComponents["slave"]["box2/" + method], bg="blue", font=("Verdana", "14", "italic"), justify='center')
                self.entryBuffer["slave"][method]["REQ"][parameter].insert(0, self.slaveBuffer[method]["REQ"][parameter]["PAR"])

                self.linkComponents["slave"]["Label/" + method + parameter].pack(fill=BOTH, expand=True)
                self.entryBuffer["slave"][method]["REQ"][parameter].pack(fill=X, expand=True)

            if self.slaveBuffer[method]["RES"] != {}:
                self.linkComponents["slave"]["response/" + method] = Label(self.linkComponents["slave"]["box2/" + method], text="RESPONSE", font=("Verdana", "16", "italic", "bold"))
                self.linkComponents["slave"]["response/" + method].pack(fill=BOTH, expand=True)
            self.entryBuffer["slave"][method]["RES"] = dict()
            for parameter in self.slaveBuffer[method]["RES"]:
                self.linkComponents["slave"]["Label/" + method + parameter] = Label(self.linkComponents["slave"]["box2/" + method], text=parameter, bg="orange", font=("Verdana", "16", "italic", "bold"))

                self.entryBuffer["slave"][method]["RES"][parameter] = Entry(self.linkComponents["slave"]["box2/" + method], bg="blue", font=("Verdana", "14", "italic"), justify='center')
                self.entryBuffer["slave"][method]["RES"][parameter].insert(0, self.slaveBuffer[method]["RES"][parameter]["PAR"])

                self.linkComponents["slave"]["Label/" + method + parameter].pack()
                self.entryBuffer["slave"][method]["RES"][parameter].pack(fill=X, expand=True)
        self.linkComponents["slave"]["scrollFrame"].pack(side=RIGHT, fill="both", expand=True)

        '''.................................................MASTER WINDOW...........................................'''

        self.linkComponents["master"]["scrollFrame"] = ScrollFrame(self.masterWindow)
        self.linkComponents["master"]["frame/master"] = Frame(self.linkComponents["master"]["scrollFrame"].viewPort)
        self.linkComponents["master"]["label/master"] = Label(self.linkComponents["master"]["frame/master"], text="Master " + list(self.master)[0], font=("Verdana", "24", "italic", "bold"), bg="purple")
        self.linkComponents["master"]["frame/master"].pack(side=LEFT, fill=BOTH, expand=True)
        self.linkComponents["master"]["label/master"].pack(fill=BOTH, expand=True)
        for method in self.masterBuffer:
            self.linkComponents["master"]["frame/" + method] = Frame(self.linkComponents["master"]["frame/master"], highlightbackground="black", highlightthickness=1, bg="green")
            self.linkComponents["master"]["box1/" + method] = Frame(self.linkComponents["master"]["frame/" + method], highlightbackground="black", highlightthickness=1,  bg="green")
            self.linkComponents["master"]["Label/" + method] = Label(self.linkComponents["master"]["box1/" + method], text=method, bg="green", font=("Verdana", "16", "italic", "bold"))

            self.entryBuffer["master"][method] = dict()
            self.entryBuffer["master"][method]["KEY"] = Entry(self.linkComponents["master"]["box1/" + method], bg="blue", font=("Verdana", "14", "italic"), justify='center')
            self.entryBuffer["master"][method]["KEY"].insert(0, self.masterBuffer[method]["KEY"])

            self.linkComponents["master"]["frame/" + method].pack(fill=BOTH, expand=True)
            self.linkComponents["master"]["box1/" + method].pack(side=LEFT, fill=BOTH, expand=True)
            self.linkComponents["master"]["Label/" + method].pack(fill=BOTH, expand=True)
            self.entryBuffer["master"][method]["KEY"].pack(fill=X, expand=True)

            self.linkComponents["master"]["box2/" + method] = Frame(self.linkComponents["master"]["frame/" + method], highlightbackground="black", highlightthickness=1, bg="orange")
            self.linkComponents["master"]["box2/" + method].pack(side=RIGHT, fill=BOTH, expand=True)

            if self.masterBuffer[method]["REQ"] != {}:
                self.linkComponents["master"]["request/" + method] = Label(self.linkComponents["master"]["box2/" + method], text="REQUESTS", font=("Verdana", "16", "italic", "bold"))
                self.linkComponents["master"]["request/" + method].pack(fill=BOTH, expand=True)
            self.entryBuffer["master"][method]["REQ"] = dict()
            for parameter in self.masterBuffer[method]["REQ"]:
                self.linkComponents["master"]["Label/" + method + parameter] = Label(self.linkComponents["master"]["box2/" + method], text=parameter, bg="orange", font=("Verdana", "16", "italic", "bold"), highlightbackground="black", highlightthickness=1)

                self.entryBuffer["master"][method]["REQ"][parameter] = Entry(self.linkComponents["master"]["box2/" + method], bg="blue", font=("Verdana", "14", "italic"), justify='center')
                self.entryBuffer["master"][method]["REQ"][parameter].insert(0, self.masterBuffer[method]["REQ"][parameter]["PAR"])

                self.linkComponents["master"]["Label/" + method + parameter].pack(fill=BOTH, expand=True)
                self.entryBuffer["master"][method]["REQ"][parameter].pack(fill=X, expand=True)

            if self.masterBuffer[method]["RES"] != {}:
                self.linkComponents["master"]["response/" + method] = Label(self.linkComponents["master"]["box2/" + method], text="RESPONSE", font=("Verdana", "16", "italic", "bold"))
                self.linkComponents["master"]["response/" + method].pack(fill=BOTH, expand=True)
            self.entryBuffer["master"][method]["RES"] = dict()
            for parameter in self.masterBuffer[method]["RES"]:
                self.linkComponents["master"]["Label/" + method + parameter] = Label(self.linkComponents["master"]["box2/" + method], text=parameter, bg="orange", font=("Verdana", "16", "italic", "bold"))
                self.entryBuffer["master"][method]["RES"][parameter] = Entry(self.linkComponents["master"]["box2/" + method], bg="blue", font=("Verdana", "14", "italic"), justify='center')
                self.entryBuffer["master"][method]["RES"][parameter].insert(0, self.masterBuffer[method]["RES"][parameter]["PAR"])

                self.linkComponents["master"]["Label/" + method + parameter].pack(fill=BOTH, expand=True)
                self.entryBuffer["master"][method]["RES"][parameter].pack(fill=X, expand=True)
        self.linkComponents["master"]["scrollFrame"].pack(side=LEFT, fill="both", expand=True)
        # print("entry buffer: ", self.entryBuffer)
        self.linkComponents["linkButton"] = Button(self.masterWindow, text="CLICK\nPARA\nFINALIZAR", command=lambda: self.linkRegister())
        self.linkComponents["linkButton"].pack(side=BOTTOM, fill=BOTH, expand=True)

    def linkRegister(self):
        for method in self.masterBuffer:
            self.masterBuffer[method]["KEY"] = int(self.entryBuffer["master"][method]["KEY"].get())
            for parameter in self.masterBuffer[method]["REQ"]:
                self.masterBuffer[method]["REQ"][parameter]["PAR"] = self.entryBuffer["master"][method]["REQ"][parameter].get()
            for parameter in self.masterBuffer[method]["RES"]:
                self.masterBuffer[method]["RES"][parameter]["PAR"] = self.entryBuffer["master"][method]["RES"][parameter].get()

        for method in self.slaveBuffer:
            self.slaveBuffer[method]["KEY"] = int(self.entryBuffer["slave"][method]["KEY"].get())
            for parameter in self.slaveBuffer[method]["REQ"]:
                self.slaveBuffer[method]["REQ"][parameter]["PAR"] = self.entryBuffer["slave"][method]["REQ"][parameter].get()
            for parameter in self.slaveBuffer[method]["RES"]:
                self.slaveBuffer[method]["RES"][parameter]["PAR"] = self.entryBuffer["slave"][method]["RES"][parameter].get()

        devicesToSave = dict()
        devicesToSave["slave"] = self.slave
        devicesToSave["master"] = self.master

        for component in self.linkComponents["master"]:
            self.linkComponents["master"][component].destroy()

        for component in self.linkComponents["slave"]:
            self.linkComponents["slave"][component].destroy()

        for component in self.windowComponents:
                self.windowComponents[component].destroy()

        self.linkComponents["linkButton"].destroy()

        self.request_action("linkRegister", devicesToSave)

        # print("windowWay: ", self.windowComponents)
        # self.windowWay()

    @MicroService.action
    def newId(self, service, data):
        # print("\nid: " + data["id"])
        print("newID")
        MsgBox = messagebox.askokcancel('Cadastro de Dispositivo',
                                        'Favor cadastrar o id "%s" no novo dispositivo'%data["id"])
        if MsgBox:
            messagebox.showinfo('Status', 'AGUARDANDO RESPOSTA DO DISPOSITIVO')
            self.newDevice["id"] = data["id"]
            self.request_action("getNewDevice", self.newDevice)

    @MicroService.action
    def status(self, service, data):
        print("status")
        # print(data["structure"])
        # print(self.windowComponents)
        self.structure = data["structure"]
        self.structBuffer = self.structure
        for way in self.newDevice["way"]:
            self.structBuffer = self.structBuffer[way]
        for component in self.windowComponents:
            self.windowComponents[component].destroy()
        # print("windowWay: ", self.windowComponents)
        self.windowWay()
        messagebox.showinfo('Status', data["status"])

    @MicroService.action
    def statusInfo(self, service, data):
        print("statusinfo")
        messagebox.showinfo('Status', data["status"])

    @MicroService.action
    def link(self, service, data):
        print("link")
        # print("slave: ", data["slave"])
        # print("master: ", data["master"])

        for component in self.windowComponents:
            self.windowComponents[component].destroy()

        self.master = data["master"]
        self.slave = data["slave"]
        self.linkScreen()


    @MicroService.task
    def do_anything(self):
        pass


master = Tk()

app = App(master)
master.mainloop()

