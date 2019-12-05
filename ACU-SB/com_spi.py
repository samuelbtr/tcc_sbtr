import spidev


BUS = 0
DEV = 0
TRASH_Clock = 0x00


spi = spidev.SpiDev()
spi.open(BUS, DEV) #spidev0.0

spi.max_speed_hz = 10000000
spi.mode = 0b00


#beginner ADE9000


def sep_bytes(command_list):
    
    if len(command_list) == 4:
        byte_1 = int(command_list[0]+command_list[1], 16)
        byte_0 = int(command_list[2]+command_list[3], 16)
        return byte_1, byte_0
    
    if len(command_list) == 8:
        byte_3 = int(command_list[0]+command_list[1], 16)
        byte_2 = int(command_list[2]+command_list[3], 16)
        byte_1 = int(command_list[4]+command_list[5], 16)
        byte_0 = int(command_list[6]+command_list[7], 16)
        return byte_3, byte_2, byte_1, byte_0

def read_ADE_32(addr):
    
    addr_str = format(addr, '03x')+'8'
    byte_msb, byte_lsb = sep_bytes(addr_str)
    com_hdr = [byte_msb, byte_lsb, TRASH_Clock, TRASH_Clock, TRASH_Clock, TRASH_Clock]
    ##descomentar para teste##
    #rec = [byte_msb, byte_lsb, 0x00, 0x00, 0x00, 0x00]  
    rec = spi.xfer(com_hdr, 20000, 1000, 8)
    value = 0x00
    for i in range(2, len(rec), 1):
        value = (rec[i]<<(24-(8*(i-2))))|value
    #print(rec)
    return value 

def read_ADE_16(addr):

    addr_str = format(addr, '03x')+'8'
    byte_msb, byte_lsb = sep_bytes(addr_str)
    com_hdr = [byte_msb, byte_lsb, TRASH_Clock, TRASH_Clock]
    ##descomentar para teste##
    #rec = [byte_msb, byte_lsb, 89, 78]  
    rec = spi.xfer(com_hdr, 20000, 1000, 8)
    value = 0x00
    for i in range(2, len(rec), 1):
        value = (rec[i]<<(8-(8*(i-2))))|value
    #print(rec)
    return value


def write_32_ADE(addr, value):
    addr_str = format(addr, '03x')+'0'
    value_str = format(value, '08x')
    
    com_byte_msb, com_byte_lsb = sep_bytes(addr_str)
    byte_value_3, byte_value_2, byte_value_1, byte_value_0 = sep_bytes(value_str)

    com_hdr = [com_byte_msb, com_byte_lsb, byte_value_3, byte_value_2, byte_value_1, byte_value_0]

    spi.xfer(com_hdr, 20000, 1000, 8)
    
    return read_ADE_32(addr)

def write_16_ADE(addr, value):
    adress_str = format(addr, '03x')+'0'
    value_str = format(value, '04x')

    com_byte_msb, com_byte_lsb = sep_bytes(adress_str)
    byte_value_1, byte_value_0 = sep_bytes(value_str)
    
    com_hdr = [com_byte_msb, com_byte_lsb, byte_value_1, byte_value_0]

    spi.xfer(com_hdr, 20000, 1000, 8)
    
    return read_ADE_32(addr)

'''
write_16_ADE(480, 1) #inicializar as leituras

while(True):
    
    print('########')
    print ('Endereco:')
    addr = int(input(), 16)
    print(read_ADE_32(addr))
    print('########')
    
'''