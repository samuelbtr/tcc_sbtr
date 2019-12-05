'''**********************IMPORTS***********************'''
import json
import time
from ade_regs import *
from com_spi import *
from registers_ade9000 import *
from pyfase import MicroService

class ADE9000Class(MicroService):
    def __init__(self):
        super(ADE9000Class, self).__init__(self, sender_endpoint='ipc:///tmp/sender', receiver_endpoint='ipc:///tmp/receiver')

        '''**********************ATTRIBUTES***********************'''

        self.VAL_RUN = 0x1
        self.VAL_STOP = 0x0
        self.EGY_TIME_ON = 0X01
        self.MODE_RESET = 0x21

        self.config = dict()

        self.VRMS_CTE = 52702092.0  #the digital conversion constant of tesion
        self.IRMS_CTE = 52702092.0  #the digital conversion constant of current
        self.WATT_CTE = 20694066.0  #the digital conversion constant of power
        self.WATTH_CTE = 72752621252.0  #the digital conversion constant of energy
        self.PF_CTE = 1/134217727.0 #the digital conversion constant of power factor
        self.FE_VRMS = 300  #voltage scale background

        self.ctv = 1    #voltage conversion constant initialization
        self.cti = 1    #current conversion constant initialization
        self.ctp = 1    #power conversion constant initialization
        self.cte = 1    #energy conversion constant initialization

        self.timepub = int()    #publish time range constant
        self.c_timer = 0    #publish time range auxiliar constant

        #energy accumulation variables
        self.awatth = 0
        self.avah = 0
        self.avarh = 0
        self.bwatth = 0
        self.bvah = 0
        self.bvarh = 0
        self.cwatth = 0
        self.cvah = 0
        self.cvarh = 0
        

    '''**********************FUNCTIONS**********************'''

    def on_connect(self):
        print('### on_connect ###')

    def on_new_service(self, service, actions):
        print('### on_new_service ### service: %s - actions: %s' % (service, actions))

    def on_response(self, service, data):
        print('### on_response ### service: %s respond an status of the action save_data previous resquested: %s' % (
        service, data))

    def init_UMA(self):
        write_16_ADE(ADDR_RUN, 0x0) #Stop
        write_16_ADE(ADDR_ACCMODE, 0x100)   #sets the default frequency to 60 Hz
        write_16_ADE(ADDR_EGY_TIME, 0x1f3f) #Energy accumulation samples
        write_16_ADE(ADDR_EP_CFG, 0x11) #Energy accumulation ON
        write_32_ADE(ADDR_CNFG0, 0x820)
        write_16_ADE(ADDR_PGA, 0x3f) #Current PGA Gain 
        write_32_ADE(ADDR_DICOEFF,0xffffe000) 
        write_16_ADE(ADDR_RUN, 0x1) #RUN
        
        self.constantRefresh()

        f = open("cali_values.json", "r")
        cali_values = json.loads(f.read())
        f.close()

        buf = ""
        for cali in cali_values:
            write_32_ADE(int(cali, 0), int(cali_values[cali], 0))
            time.sleep(1/1000)
            buf += cali + ":" +hex(read_ADE_32(int(cali, 0))) + " "
        print(buf+"\n")

    def twos_compliment(self, bitreg32):
        if bitreg32 > 0x7fffffff:
            return -1*(0xffffffff - bitreg32 + 1)
        else:
            return bitreg32

    def constantRefresh(self):
        f = open("config.json", "r")
        self.config = json.loads(f.read())
        f.close()

        self.timepub = float(self.config["timepub"])

        self.ctv = self.config["FT_MULTI_TP"] * self.FE_VRMS / self.VRMS_CTE
        self.cti = self.config["FE_IRMS"] * self.config["FS"] / self.IRMS_CTE
        self.ctp = self.config["FE_IRMS"] * self.config["FS"] * self.config["FT_MULTI_TP"] * self.FE_VRMS / self.WATT_CTE
        self.cte = self.config["FE_IRMS"] * self.config["FS"] * self.config["FT_MULTI_TP"] * self.FE_VRMS / self.WATTH_CTE

    def negativetozero(self, n):
        if n < 0:
            return -n
        else:
            return n

    def readADE9000(self):
        energy = {}

        '''**********************ACQUIRE AC POWER DATA PHASE*************************'''
        energy["avrms"] = self.negativetozero(read_ADE_32(ADDR_AVRMS1012)*self.ctv)
        energy["airms"] = self.negativetozero(read_ADE_32(ADDR_AIRMS1012)*self.cti)
        energy["apf"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_APF)) * self.PF_CTE)
        energy["awatt"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_AWATT)) * self.ctp)
        energy["ava"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_AVA)) * self.ctp)
        energy["avar"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_AVAR)) * self.ctp)
        energy["awatth"] = self.negativetozero(self.awatth)
        energy["avah"] = self.negativetozero(self.avah)
        energy["avarh"] = self.negativetozero(self.avarh)
        self.awatth = 0
        self.avah = 0
        self.avarh = 0

        '''**********************ACQUIRE AC POWER DATA PHASE*************************'''
        energy["bvrms"] = self.negativetozero(read_ADE_32(ADDR_BVRMS1012) * self.ctv)
        energy["birms"] = self.negativetozero(read_ADE_32(ADDR_BIRMS1012) * self.cti)
        energy["bpf"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_BPF)) * self.PF_CTE)
        energy["bwatt"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_BWATT)) * self.ctp)
        energy["bva"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_BVA)) * self.ctp)
        energy["bvar"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_BVAR)) * self.ctp)
        energy["bwatth"] = self.negativetozero(self.bwatth)
        energy["bvah"] = self.negativetozero(self.bvah)
        energy["bvarh"] = self.negativetozero(self.bvarh)
        self.bwatth = 0
        self.bvah = 0
        self.bvarh = 0

        '''**********************ACQUIRE AC POWER DATA PHASE*************************'''
        energy["cvrms"] = self.negativetozero(read_ADE_32(ADDR_CVRMS1012) * self.ctv)
        energy["cirms"] = self.negativetozero(read_ADE_32(ADDR_CIRMS1012) * self.cti)
        energy["cpf"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_CPF)) * self.PF_CTE)
        energy["cwatt"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_CWATT)) * self.ctp)
        energy["cva"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_CVA)) * self.ctp)
        energy["cvar"] = self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_CVAR)) * self.ctp)
        energy["cwatth"] = self.negativetozero(self.cwatth)
        energy["cvah"] = self.negativetozero(self.cvah)
        energy["cvarh"] = self.negativetozero(self.cvarh)
        self.cwatth = 0
        self.cvah = 0
        self.cvarh = 0

        #print(energy)

        return energy

    def energy_ACC(self):
        self.awatth += self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_AWATTHR_HI)) * self.cte)
        self.bwatth += self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_BWATTHR_HI)) * self.cte)
        self.cwatth += self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_CWATTHR_HI)) * self.cte)

        self.avah += self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_AVAHR_HI)) * self.cte)
        self.bvah += self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_BVAHR_HI)) * self.cte)
        self.cvah += self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_CVAHR_HI)) * self.cte)

        self.avarh += self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_AVARHR_HI)) * self.cte)
        self.bvarh += self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_BVARHR_HI)) * self.cte)
        self.cvarh += self.negativetozero(self.twos_compliment(read_ADE_32(ADDR_CVARHR_HI)) * self.cte)

    @MicroService.action
    def refresh(self, service, data):
        self.constantRefresh()

    @MicroService.action
    def measurement(self, service, data):
        print(data)
        measure = self.readADE9000()
        self.request_action('mqtt_publish', measure)

    
    @MicroService.task
    def publish(self):
        self.init_UMA()
        self.constantRefresh()
        while True:
            self.energy_ACC()
            time.sleep(1)

    '''
        #tempo = time.time()
        while True:

            if self.c_timer >= self.timepub:
                measure = self.readADE9000()
                self.request_action('mqtt_publish', measure)
                #print(measure)
                #print(self.c_timer)
                self.c_timer = 0
                tempo = time.time()
            #print(time.time()-tempo)
            self.energy_ACC()
            time.sleep(1)
            self.c_timer += 1

   '''
ADE9000Class().execute(enable_tasks=True)
