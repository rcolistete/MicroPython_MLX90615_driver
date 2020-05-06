"""
MicroPython driver for MLX90615 IR temperature I2C sensor :
https://github.com/rcolistete/MicroPython_MLX90615_driver
Version for BBC Micro:bit without error checking : 0.2.1 @ 2020/05/04
Author: Roberto Colistete Jr. (roberto.colistete at gmail.com)
License: MIT License (https://opensource.org/licenses/MIT)
"""

__version__ = '0.2.1'


from micropython import const
import time


MLX90615_I2C_DEFAULT_ADDR = const(0x5B)
EEPROM_DEFAULT_TIME_MS = const(50)     # erase/write EEPROM time in ms

_REG_SLAVE_I2C_ADDRESS = const(0x10)   # EEPROM register - slave I2C address
_REG_EMISSIVITY = const(0x13)          # EEPROM register - Emissivity
_REG_ID_LOW = const(0x1E)              # EEPROM register - ID number low
_REG_ID_HIGH = const(0x1F)             # EEPROM register - ID number high
_REG_RAW_IR_DATA = const(0x25)         # RAM register - raw IR data register
_REG_AMBIENT_TEMP = const(0x26)        # RAM register - ambient temperature register
_REG_OBJECT_TEMP  = const(0x27)        # RAM register - object temperature register 


class MLX90615:
    def __init__(self, i2c, address=MLX90615_I2C_DEFAULT_ADDR):
        self.i2c = i2c
        self.address = address
        self.register_buf = bytearray(1)
        self.buf = bytearray(3)

    def _crc8(self, icrc, data):
        crc = icrc ^ data
        for _ in range(8):
            crc <<= 1
            if crc & 0x0100:
                crc ^= 0x07
            crc &= 0xFF
        return crc

    def read16(self, register):
        self.register_buf[0] = register
        self.i2c.write(self.address, self.register_buf, repeat=True)
        self.buf =	self.i2c.read(self.address, 3, repeat=True)
        lsb = self.buf[0]
        msb = self.buf[1]
        return lsb | (msb << 8)

    def write16(self, register, data, eeprom_time=EEPROM_DEFAULT_TIME_MS):
        lsb = data & 0x00FF
        msb = data >> 8        
        crc = self._crc8(0, self.address << 1)
        crc = self._crc8(crc, register)
        crc = self._crc8(crc, lsb)
        crc = self._crc8(crc, msb)
        self.i2c.write(self.address, bytearray([register, lsb, msb, crc]), repeat=True)   
        time.sleep_ms(eeprom_time)

    def read_ambient_temp(self):
        return (self.read16(_REG_AMBIENT_TEMP))*2 - 27315

    def read_object_temp(self):
        return (self.read16(_REG_OBJECT_TEMP))*2 - 27315

    def read_raw_ir_data(self):
        return self.read16(_REG_RAW_IR_DATA)

    def read_id(self):
        return self.read16(_REG_ID_LOW) | (self.read16(_REG_ID_HIGH) << 16)

    def read_eeprom(self):
        eeprom_data = [0]*0x10
        for register in range(0x10, 0x20):
            eeprom_data[register - 0x10] = self.read16(register)
        return eeprom_data

    def read_emissivity(self):
        d = self.read16(_REG_EMISSIVITY)
        if (d >= 32768):
            d = 32768 - d
        return round(100*d/0x4000)

    def set_emissivity(self, value=100, eeprom_write_time=EEPROM_DEFAULT_TIME_MS):
        if (value >= 5) and (value <= 100):
            e = round((value*0x4000)/100)
            time.sleep_ms(eeprom_write_time)
            self.write16(_REG_EMISSIVITY, 0x0000, eeprom_time=eeprom_write_time)
            time.sleep_ms(eeprom_write_time)
            self.write16(_REG_EMISSIVITY, e, eeprom_time=eeprom_write_time)
            time.sleep_ms(eeprom_write_time)

    def read_i2c_address(self):
        return self.read16(_REG_SLAVE_I2C_ADDRESS) & 0x007F

    def set_i2c_address(self, addr=0x5B, eeprom_write_time=EEPROM_DEFAULT_TIME_MS):
        if self.address == 0:
            if (addr >= 0x08) and (addr <= 0x77):
                d = 0x3500 | addr       
                time.sleep_ms(eeprom_write_time)
                self.write16(_REG_SLAVE_I2C_ADDRESS, 0x0000, eeprom_time=eeprom_write_time)
                time.sleep_ms(eeprom_write_time)
                self.write16(_REG_SLAVE_I2C_ADDRESS, d, eeprom_time=eeprom_write_time)
                time.sleep_ms(eeprom_write_time)
