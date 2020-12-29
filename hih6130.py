import time
import smbus

TEMPERATURE_REG = 0x00
CONFIG_REG = 0x01
T_LOW_REG = 0x02
T_HIGH_REG = 0x03

ADDRESSES = [0x27]

class HIH6130(object):
    def __init__(self, address=0x27, busnum=1):
        self.address = address
        self.busnum = busnum

        self.bus = smbus.SMBus(self.busnum)

    def readTemperature(self):
        # Measurement Request is initiated by sending a write bit 
        self.bus.write_quick(self.address) 
        # It takes about 30ms to generate results
        #time.sleep(0.05)
        # Begin reading
        result = self.bus.read_i2c_block_data(self.address, 0x00, 4)
        # Check status
        status = result[0] >> 6 & 0x03 
        #print("Status is {} (0 new data, 1 stale)".format(status))
        rh = round(((result[0] & 0x3f) << 8 | result[1]) * 100.0 / (2**14 - 1), 2)
        t = round((float((result[2] << 6) + (result[3] >> 2)) / (2**14 - 1)) * 165.0 - 40, 2)+273.15
        return (t,rh)
